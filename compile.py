from beet import Context

from src.python.config import PyriscvConfig, TextStoragePosition
from plugin.stage_1 import build_mcb
from plugin.auto_dollor import auto_dollor
from plugin.stage_2 import load_memory_file


def main(ctx: Context):
    config = PyriscvConfig()
    # config.stage_2_cache = False
    config.text_storage_position = TextStoragePosition.MINECRAFT_FUNCTION
    config.set_expand_instruction_function(
        ["add", "addi", "sub", "lui", "auipc", "jal", "mul"]
    )

    build_mcb(ctx, config)
    print("Stage 1 Done.")

    load_memory_file(ctx, "/mnt/e/code/pyriscv/app/minecraft-1960-c/app.mem", config)
    # load_memory_file(
    #     ctx, "./app/cpp-eliza/dump.txt", config, "./app/cpp-eliza/dump-reg.txt"
    # )
    # load_memory_file(ctx, "./app/cpp-stream/app.mem", config)
    # load_memory_file(ctx, "./app/c-miniMNIST/app.mem", config)

    # Warning! This freak will prepend dollar signs to a certain range of functions
    # So if you are writing some "$(" which do not stand for a marco, be careful!
    auto_dollor(ctx, config)

    print("Stage 2 Done.")
