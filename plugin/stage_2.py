import hashlib
import shutil

from beet import Context

from src.python.memory import *
from src.python.encoder import encode_to_scoreboard, encode_to_function
from src.python.decoder import PyriscvDecodedInstruction
from src.python.config import *


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
    instruction_mcbuild_functions_dir = ctx.cache["riscvmc2-stage-2"].directory / "mcbuild"

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

    # load text sector

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
