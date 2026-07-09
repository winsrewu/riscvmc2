from beet import Context, Function

from src.python.config import PyriscvConfig

def append_auto_dollar(function: Function):
    for i in range(len(function.lines)):
        if "$(" in function.lines[i] and not (
            function.lines[i].startswith("$") and not function.lines[i].startswith("$(")
        ):
            function.lines[i] = "$" + function.lines[i]


def auto_dollor(ctx: Context, config: PyriscvConfig):
    ACCEPTED_INJECT_PREFIXS = [
        "org_jawbts_riscvmc2_rv32i",
        "org_jawbts_riscvmc2_rv32m",
        "org_jawbts_riscvmc2_memory",
        "org_jawbts_riscvmc2_test",
    ]

    ACCEPTED_INJECT_PREFIXS.append(config.instruction_namespace)
    
    functions = ctx.data.functions
    for key, func in functions.items():
        if any(key.startswith(prefix) for prefix in ACCEPTED_INJECT_PREFIXS):
            append_auto_dollar(func)
