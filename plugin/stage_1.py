import os
import re
import shutil
import json
import subprocess
from beet import Context

from src.python.config import PyriscvConfig, TextStoragePosition

MCB_CONFIG_FILE = "mcb.config.js"
INSTRUCTION_STANDALONE_MCB_IMPORT = "import ./org_jawbts_riscvmc2_rv32i_t.mcbt\n" \
                                    "import ./org_jawbts_riscvmc2_rv32m_t.mcbt\n" \
                                    "import ./org_jawbts_riscvmc2_memory_t.mcbt\n"


def extract_inst_def_area(content: str):
    pattern = r"(# #BEGIN INST DEF\n.*?\n# #END INST DEF)"

    m = re.search(pattern, content, re.DOTALL)
    if m is None or len(m.groups()) > 1:
        raise ValueError(f"Invalid content")

    area = m.group(1).strip()
    remaining = content.replace(m.group(1), "", 1)

    return area, remaining


def extract_inst_funct(content: str):
    """
    ```
    function <name> {
        <code>
    }
    ...
    ```
    ->
    ```
    [{
        "name": <name>,
        "code": <code>
    }, ...]
    ```
    """
    pattern = r"function\s+(\w+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"

    matches = re.findall(pattern, content, re.DOTALL)

    result = []
    for name, code in matches:
        result.append({"name": name.strip().replace("i_", ""), "code": code})

    return result


def build_mcb(ctx: Context, pyriscv_config: PyriscvConfig):
    """
    Special thanks to https://github.com/SnaveSutit/mcb-beet.
    """

    config = ctx.directory / MCB_CONFIG_FILE
    build_dir = ctx.cache["riscvmc2-stage-1"].directory / "datapack"
    source_dir = ctx.directory / "src" / "mcbuild"

    # Cleanup
    shutil.rmtree(build_dir, ignore_errors=True)

    # Copy sources
    shutil.copytree(
        source_dir / "mcb",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "lib" / "bitwise_ops" / "scoreboard",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "lib" / "ascii",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "lib" / "terminal",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "main",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "instruction" / "template",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    # Process instructions

    standalone_instructions = []
    for file in os.listdir(source_dir / "instruction" / "function"):
        with open(source_dir / "instruction" / "function" / file, "r") as f:
            content = f.read()
            inst_def, rem = extract_inst_def_area(content)
            with open(build_dir / "src" / file, "w") as f:
                f.write(rem)

            standalone_instructions += extract_inst_funct(inst_def)

    # dump it for stage 2
    with open(build_dir / "standalone_instructions.json", "w") as f:
        f.write(json.dumps(standalone_instructions))

    with open(
        build_dir / "src" / (pyriscv_config.instruction_namespace + ".mcb"), "w"
    ) as f:
        f.write(
            INSTRUCTION_STANDALONE_MCB_IMPORT
        )

        for inst in standalone_instructions:
            if not inst["name"] in pyriscv_config.instruction_function_expand:
                raise ValueError(f"Invalid instruction {inst["name"]}")
            if (
                (not pyriscv_config.instruction_function_expand[inst["name"]])
                or pyriscv_config.text_storage_position
                == TextStoragePosition.MINECRAFT_STORAGE
            ):
                f.write(f"function {inst["name"]} {{{inst["code"]}}}\n")

    # Copy debug sources
    shutil.copytree(source_dir / "test", build_dir / "src", dirs_exist_ok=True)

    # Copy & append custom config
    config_content = None
    with open(config, "r") as f:
        config_content = f.read()

    config_content = config_content.replace(
        "<% PLACEHOLDER_INSTRUCTION_NAMESPACE %>", pyriscv_config.instruction_namespace
    )
    config_content = config_content.replace(
        "<% PLACEHOLDER_INSTRUCTION_FUNCTION_NAMESPACE %>",
        pyriscv_config.instruction_function_namespace,
    )
    config_content = config_content.replace(
        "<% PLACEHOLDER_TEXT_STORAGE_POSITION %>",
        pyriscv_config.text_storage_position.name,
    )
    config_content = config_content.replace(
        '"<% PLACEHOLDER_SCREEN_ENABLED %>"',
        "true" if pyriscv_config.screen_enabled else "false",
    )

    with open(build_dir / MCB_CONFIG_FILE, "w") as f:
        f.write(config_content)

    # Create dummy pack.mcmeta
    with open(build_dir / "pack.mcmeta", "w") as f:
        meta = {"pack": {"pack_format": ctx.data.pack_format}}
        json.dump(meta, f)

    # Run mcb
    command = ["mcb", "build"]
    try:
        app = subprocess.run(
            command,
            cwd=build_dir,
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

    # Load the built datapack
    ctx.data.load(build_dir)
