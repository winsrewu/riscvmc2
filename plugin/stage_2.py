import hashlib
import json
import os
import re
import shutil
import subprocess

from beet import Context

from plugin.stage_1 import MCB_CONFIG_FILE
from src.python.memory import *
from src.python.encoder import encode_to_scoreboard, encode_to_function
from src.python.decoder import PyriscvDecodedInstruction
from src.python.config import *


def replace_placeholders(text: str, mapping: dict[str, str]):
    def replace_match(m: re.Match):
        key = m.group(1)
        if not key in mapping:
            raise ValueError(f"Unknown placeholder: {key}")
        return str(mapping[key])

    return re.sub(r"\$\(([^)]+)\)", replace_match, text)


def load_memory_file(
    ctx: Context, mem_path: str, config: PyriscvConfig, reg_path: str = None
):
    """
    Loads memory, optional registers and pc to datapack context.

    mem_path: path to a verilog format memory file
    reg_path: path to pc & registers file, format:
    ```
    0x1298      # pc
    0x0         # reg x0
    0x1288      # reg x1
    0x2204ca2c  # ...
    0x2004901a
    0x0
    0x37504
    # ...
    ```
    """

    config_changed_flag = False
    prev_config_json = ctx.cache["riscvmc2-stage-2"].json.get("config", None)
    if prev_config_json is None:
        config_changed_flag = True
    else:
        try:
            prev_config = PyriscvConfig.model_validate_json(prev_config_json)
        except ValueError:
            config_changed_flag = True
        else:
            if prev_config != config:
                config_changed_flag = True

    hasher = hashlib.sha256()
    prev_source_hash = ctx.cache["riscvmc2-stage-2"].json.get("source_hash", None)

    datapack_build_dir = ctx.cache["riscvmc2-stage-2"].directory / "datapack"
    loader_functions_dir = (
        datapack_build_dir / "data" / "org_jawbts_riscvmc2_loader" / "function"
    )
    instruction_mcbuild_functions_dir = (
        ctx.cache["riscvmc2-stage-2"].directory / "mcbuild-datapack"
    )

    with open(mem_path, "rb") as f:
        hasher.update(f.read())

    if reg_path is not None:
        with open(reg_path, "rb") as f:
            hasher.update(f.read())

    if (
        prev_source_hash == hasher.hexdigest()
        and (datapack_build_dir / "data").exists()
        and not config_changed_flag
        and config.stage_2_cache
    ):
        # uses cache
        ctx.data.load(datapack_build_dir)
        ctx.data.load(instruction_mcbuild_functions_dir)
        return

    # cleanup for rebuild

    shutil.rmtree(ctx.cache["riscvmc2-stage-2"].directory, ignore_errors=True)
    loader_functions_dir.mkdir(exist_ok=True, parents=True)
    instruction_mcbuild_functions_dir.mkdir(exist_ok=True, parents=True)

    # load & encode data sector

    mem = read_verilog_v8(mem_path, default_keep_data_section)
    dat = process_memory_into_data(mem)

    with open(loader_functions_dir / "data.mcfunction", "w") as f:
        for s in encode_to_scoreboard(dat):
            f.write(f"{s}\n")
        f.write("say Data loaded\n")

    # load text sector in MINECRAFT_STORAGE mode

    if config.text_storage_position == TextStoragePosition.MINECRAFT_STORAGE:
        mem = read_verilog_v8(mem_path, default_keep_text_section)
        res_l = []
        res = ""
        for inst, addr in process_memory_into_raw_inst(mem):
            try:
                name, arg = encode_to_function(PyriscvDecodedInstruction(inst))
            except Exception as ex:
                print("Error at address 0x%x, data 0x%x" % (int(addr), int(inst)))
                raise ex
            res += f'{addr.signed()}:"{name} {arg}",'
            if len(res) >= 10000:
                res_l.append(res)
                res = ""
        res_l.append(res)

        with open(loader_functions_dir / "text.mcfunction", "w") as f:
            for res in res_l:
                res = res[:-1]
                res = f"data modify storage org_jawbts_riscvmc2_temp:main inst merge value {{{res}}}"
                f.write(f"{res}\n")
            f.write("say Text loaded\n")

    # load text sector in MINECRAFT_FUNCTION mode

    if config.text_storage_position == TextStoragePosition.MINECRAFT_FUNCTION:
        # Copy source from stage 1
        shutil.copytree(
            ctx.cache["riscvmc2-stage-1"].directory / "datapack" / "src",
            instruction_mcbuild_functions_dir / "src",
            dirs_exist_ok=True,
        )

        shutil.copy(
            ctx.cache["riscvmc2-stage-1"].directory / "datapack" / MCB_CONFIG_FILE,
            instruction_mcbuild_functions_dir / MCB_CONFIG_FILE,
        )

        shutil.copy(
            ctx.cache["riscvmc2-stage-1"].directory / "datapack" / "pack.mcmeta",
            instruction_mcbuild_functions_dir / "pack.mcmeta",
        )

        standalone_instructions = []
        with open(
            ctx.cache["riscvmc2-stage-1"].directory
            / "datapack"
            / "standalone_instructions.json",
            "r",
        ) as f:
            standalone_instructions = json.load(f)

        standalone_instructions_map = {}
        for inst in standalone_instructions:
            standalone_instructions_map[inst["name"]] = inst["code"]

        # Inject text sector in

        mem = read_verilog_v8(mem_path, default_keep_text_section)
        with open(
            instruction_mcbuild_functions_dir
            / "src"
            / f"{config.instruction_function_namespace}.mcb",
            "w",
        ) as f:
            f.write(
                "import ./org_jawbts_riscvmc2_rv32i_t.mcbt\nimport ./org_jawbts_riscvmc2_memory_t.mcbt\n"
            )

            for inst, addr in process_memory_into_raw_inst(mem):
                try:
                    name, arg = encode_to_function(PyriscvDecodedInstruction(inst))
                except Exception as ex:
                    print("Error at address 0x%x, data 0x%x" % (int(addr), int(inst)))
                    raise ex

                if not name in config.instruction_function_expand:
                    raise ValueError(f"Invalid instruction {name}")
                if config.instruction_function_expand[name]:
                    f.write(
                        f"function {addr.unsigned()} {{{replace_placeholders(standalone_instructions_map[name], arg)}}}\n"
                    )
                else:
                    f.write(
                        f"function {addr.unsigned()} {{\n\tfunction {config.instruction_namespace}:{name} {arg}\n}}\n"
                    )

        # build mcb (SUPER SLOW, TODO: optimize)
        command = ["mcb", "build"]
        try:
            app = subprocess.run(
                command,
                cwd=instruction_mcbuild_functions_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding="utf-8",
            )
            if app.returncode != 0 or "Error" in app.stdout or "Error" in app.stderr:
                raise subprocess.CalledProcessError(
                    app.returncode, command, app.stdout, app.stderr
                )

        except subprocess.CalledProcessError as e:
            print(f"Error while running MCB: {e.stderr}")
            raise e

        # purge all stuff we don't want
        for dir in os.listdir(instruction_mcbuild_functions_dir / "data"):
            if dir != config.instruction_function_namespace:
                shutil.rmtree(instruction_mcbuild_functions_dir / "data" / dir)

        ctx.data.load(instruction_mcbuild_functions_dir)

    # load pc & registers (if provided)

    if reg_path is not None:
        with open(reg_path, "r") as f:
            pc = Operand(int(f.readline().strip(), 16)).signed()
            reg = [None] * 32
            for i in range(32):
                reg[i] = Operand(int(f.readline().strip(), 16)).signed()
            with open(loader_functions_dir / "regs.mcfunction", "w") as f:
                f.write(
                    f"scoreboard players set #pc org_jawbts_riscvmc2_register {pc}\n"
                )
                for i in range(32):
                    f.write(
                        f"scoreboard players set #{i} org_jawbts_riscvmc2_register {reg[i]}\n"
                    )
                f.write("say Registers loaded\n")

    # one-in-all function

    with open(loader_functions_dir / "all.mcfunction", "w") as f:
        f.write("function org_jawbts_riscvmc2_loader:data\n")
        f.write("function org_jawbts_riscvmc2_loader:text\n")
        if reg_path is not None:
            f.write("function org_jawbts_riscvmc2_loader:regs\n")

    # finish and save

    ctx.data.load(datapack_build_dir)
    ctx.cache["riscvmc2-stage-2"].json["source_hash"] = hasher.hexdigest()
    ctx.cache["riscvmc2-stage-2"].json["config"] = config.model_dump_json()
