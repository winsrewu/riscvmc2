from beet import Context

from src.python.config import PyriscvConfig, TextStoragePosition
from plugin.stage_1 import build_mcb
from plugin.auto_dollor import auto_dollor
from plugin.screen_gen import generate_screen
from plugin.stage_2 import load_memory_file


def main(ctx: Context):
    config = PyriscvConfig()
    config.stage_2_cache = False
    config.text_storage_position = TextStoragePosition.MINECRAFT_STORAGE
    config.set_expand_instruction_function(
        ["add", "addi", "sub", "lui", "auipc", "jal"]
    )

    build_mcb(ctx, config)
    print("Stage 1 Done.")

    # Standardized screen demo (pyriscv app/gfx-saver).  Replace with
    # your own program: it only needs to write its int[W*H] framebuffer
    # at _screen_fb and call ecall 2000 once per frame.  When changing
    # the size, rebuild the demo with the same W/H: the screen_width /
    # screen_height config used below must equal SCR_W / SCR_H in
    # pyriscv/app/gfx-saver/main.c (see PyriscvConfig.screen_width).
    load_memory_file(ctx, "pyriscv/app/gfx-saver/app.mem", config)
    # load_memory_file(ctx, "./app/cpp-stream/app.mem", config)

    # Static per-pixel compare/setblock code for the screen (ecall 2000).
    # Must run after stage 2 (adds functions to ctx.data.functions) and
    # before auto_dollor.
    generate_screen(ctx, config)

    # Warning! This freak will prepend dollar signs to a certain range of functions
    # So if you are writing some "$(" which do not stand for a marco, be careful!
    auto_dollor(ctx, config)

    print("Stage 2 Done.")
