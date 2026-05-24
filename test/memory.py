import random


def s32(v):
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v >= 0x80000000 else v


mem = {1024: 0}


def store_byte(a, v):
    v &= 0xFF
    s = 8 * (a & 3)
    mem[1024] = s32((mem[1024] & ~(0xFF << s)) | (v << s))


def store_halfword(a, v):
    v &= 0xFFFF
    for i in range(2):
        store_byte(a + i, (v >> (8 * i)) & 0xFF)


def store_word(a, v):
    for i in range(4):
        store_byte(a + i, (v >> (8 * i)) & 0xFF)


def load_byte(a, signed):
    s = 8 * (a & 3)
    val = (mem[1024] >> s) & 0xFF
    return val - 0x100 if signed and (val & 0x80) else val


def load_halfword(a, signed):
    s = 8 * (a & 3)
    val = (mem[1024] >> s) & 0xFFFF
    return val - 0x10000 if signed and (val & 0x8000) else val


def load_word(a):
    return mem[1024]


configs = {
    "save_byte": {"addrs": [1024, 1025, 1026, 1027], "load": False},
    "save_halfword": {"addrs": [1024, 1026], "load": False},
    "save_word": {"addrs": [1024], "load": False},
    "load_byte_unsigned": {
        "addrs": [1024, 1025, 1026, 1027],
        "load": True,
        "signed": False,
    },
    "load_halfword_unsigned": {"addrs": [1024, 1026], "load": True, "signed": False},
    "load_word": {"addrs": [1024], "load": True, "signed": False},
    "load_byte_signed": {
        "addrs": [1024, 1025, 1026, 1027],
        "load": True,
        "signed": True,
    },
    "load_halfword_signed": {"addrs": [1024, 1026], "load": True, "signed": True},
}

tests = [name for name in configs for _ in range(50)]
random.shuffle(tests)

out = [
    "import ./org_jawbts_riscvmc2_memory_t.mcbt",
    "function test {",
    "\tscoreboard players set #1024 org_jawbts_riscvmc2_memory 0",
]
count = 0

for instr in tests:
    cfg = configs[instr]
    addr = random.choice(cfg["addrs"])
    val = random.randint(-(2**31), 2**31 - 1)

    out.append(f"\tscoreboard players set #1 test {addr}")

    if not cfg["load"]:
        out.append(f"\tscoreboard players set #2 test {val}")
        if instr == "save_byte":
            cmd = "template save_byte #1@test #2@test"
            store_byte(addr, val)
        elif instr == "save_halfword":
            cmd = "template save_halfword #1@test #2@test"
            store_halfword(addr, val)
        elif instr == "save_word":
            cmd = "template save_word #1@test #2@test"
            store_word(addr, val)
        out.append(f"\t{cmd}")
    else:
        out.append("\tscoreboard players set #2 test 0")
        signed = cfg["signed"]
        if "byte" in instr:
            cmd = f"template load_byte #1@test #2@test {'signed' if signed else 'unsigned'}"
            exp = load_byte(addr, signed)
        elif "halfword" in instr:
            cmd = f"template load_halfword #1@test #2@test {'signed' if signed else 'unsigned'}"
            exp = load_halfword(addr, signed)
        else:
            cmd = "template load_word #1@test #2@test"
            exp = load_word(addr)
        out.append(f"\t{cmd}")
        count += 1
        out.append(
            f"\texecute unless score #2 test matches {exp} run say !!ERROR {count} !!"
        )

out.append("\tsay Finished.")
out.append("}")
print("\n".join(out))
