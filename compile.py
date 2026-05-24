from beet import Context

from plugin.mcbuild import build_mcb
from plugin.auto_dollor import auto_dollor
from plugin.loader import load_memory_file


def main(ctx: Context):
    build_mcb(ctx)

    # Warning! This freak will prepend dollar signs to a certain range of functions
    # So if you are writing some "$(" which do not stand for a marco, be careful!
    auto_dollor(ctx)

    # load_memory_file(ctx, "./app/cpp-eliza/dump.txt", "./app/cpp-eliza/dump-reg.txt")
    load_memory_file(ctx, "./app/cpp-stream/app.mem")

    print("Done.")
