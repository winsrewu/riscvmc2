# python bitwise_ops.py > ..\src\mcbuild\test\test.mcb
# bullshit wrote by a LLM

import random
import os


def to_int32(n):
    n &= 0xFFFFFFFF
    return n - 0x100000000 if n > 0x7FFFFFFF else n


SB = "org_jawbts_riscvmc2_register"
NS = "org_jawbts_riscvmc2_rv32i"


def p(s):
    print("\t" + s)


def gen():
    ops = [
        ("add", "R", lambda a, b: to_int32(a + b)),
        ("sub", "R", lambda a, b: to_int32(a - b)),
        ("and", "R", lambda a, b: to_int32(a & b)),
        ("or", "R", lambda a, b: to_int32(a | b)),
        ("xor", "R", lambda a, b: to_int32(a ^ b)),
        ("sll", "R", lambda a, b: to_int32(a << (b & 0x1F))),
        ("srl", "R", lambda a, b: to_int32((a & 0xFFFFFFFF) >> (b & 0x1F))),
        ("sra", "R", lambda a, b: to_int32(a >> (b & 0x1F))),
        ("addi", "I", lambda a, i: to_int32(a + i)),
        ("andi", "I", lambda a, i: to_int32(a & i)),
        ("ori", "I", lambda a, i: to_int32(a | i)),
        ("xori", "I", lambda a, i: to_int32(a ^ i)),
        ("slti", "I", lambda a, i: 1 if a < i else 0),
        ("sltiu", "I", lambda a, i: 1 if (a & 0xFFFFFFFF) < (i & 0xFFFFFFFF) else 0),
        ("lui", "U", lambda i: to_int32(i)),
        ("auipc", "U", lambda i, pc: to_int32(i + pc)),
        ("slt", "R", lambda a, b: 1 if a < b else 0),
        ("sltu", "R", lambda a, b: 1 if (a & 0xFFFFFFFF) < (b & 0xFFFFFFFF) else 0),
    ]

    branches = [
        ("beq", lambda a, b: a == b),
        ("bne", lambda a, b: a != b),
        ("bge", lambda a, b: a >= b),
        ("bgeu", lambda a, b: (a & 0xFFFFFFFF) >= (b & 0xFFFFFFFF)),
        ("blt", lambda a, b: a < b),
        ("bltu", lambda a, b: (a & 0xFFFFFFFF) < (b & 0xFFFFFFFF)),
    ]

    jumps = ["jal", "jalr"]

    for name, typ, logic in ops:
        p(f"# {name}")
        for i in range(1000):
            rd = random.randint(0, 31)
            rs1 = random.randint(0, 31)

            if typ == "R":
                rs2 = random.randint(0, 30)
                if rs2 >= rs1:
                    rs2 += 1
            else:
                rs2 = random.randint(0, 31)

            v1 = random.randint(-2147483648, 2147483647)
            v2 = random.randint(-2147483648, 2147483647)

            if typ == "I":
                raw_imm = random.randint(-2048, 2047)
                proc_imm = to_int32(raw_imm)
            elif typ == "U":
                raw_imm = random.randint(0, 0xFFFFF)
                proc_imm = to_int32(raw_imm << 12)
            else:
                proc_imm = v2

            if "shift" in name:
                proc_imm &= 0x1F
                raw_imm = proc_imm

            if rs1 != 0:
                p(f"scoreboard players set #{rs1} {SB} {v1}")
            if rs2 != 0 and typ == "R":
                p(f"scoreboard players set #{rs2} {SB} {v2}")

            if typ == "R":
                exp = logic(v1 if rs1 != 0 else 0, v2 if rs2 != 0 else 0)
            elif typ == "I":
                exp = logic(v1 if rs1 != 0 else 0, proc_imm)
            elif typ == "U":
                if name == "auipc":
                    current_pc = 10000 + i * 4
                    p(f"scoreboard players set #pc {SB} {current_pc}")
                    exp = logic(proc_imm, current_pc)
                else:
                    exp = logic(proc_imm)

            rd_target = "trash_bin" if rd == 0 else str(rd)
            call = f"function {NS}:i_{name} {{"
            if typ == "R":
                call += f'rs1:"{rs1}",rs2:"{rs2}",rd:"{rd_target}"'
            elif typ == "I":
                call += f'rs1:"{rs1}",rd:"{rd_target}",imm:"{proc_imm}"'
            elif typ == "U":
                call += f'rd:"{rd_target}",imm:"{proc_imm}"'
            call += "}"
            p(call)

            tgt = "trash_bin" if rd == 0 else rd
            p(
                f"execute unless score #{tgt} {SB} matches {exp} run say FAIL:{name}:{rd}:exp:{exp} {os.urandom(4).hex()}"
            )

    for name, logic in branches:
        p(f"# {name}")
        for i in range(1000):
            rs1 = random.randint(0, 31)
            rs2 = random.randint(0, 30)
            if rs2 >= rs1:
                rs2 += 1

            v1 = random.randint(-2147483648, 2147483647)
            v2 = random.randint(-2147483648, 2147483647)
            imm = random.randint(-100, 100) * 4
            pc_start = 20000 + i * 4

            if rs1 != 0:
                p(f"scoreboard players set #{rs1} {SB} {v1}")
            if rs2 != 0:
                p(f"scoreboard players set #{rs2} {SB} {v2}")

            p(f"scoreboard players set #pc {SB} {pc_start}")

            taken = logic(v1 if rs1 != 0 else 0, v2 if rs2 != 0 else 0)
            pc_exp = pc_start + imm if taken else pc_start + 4

            p(f'function {NS}:i_{name} {{rs1:"{rs1}",rs2:"{rs2}",imm:"{imm}"}}')
            p(
                f"execute unless score #pc {SB} matches {pc_exp} run say FAIL:{name}:exp:{pc_exp} {os.urandom(4).hex()}"
            )

    for name in jumps:
        p(f"# {name}")
        for i in range(1000):
            rs1 = random.randint(0, 31)
            rd = random.randint(0, 31)
            v1 = random.randint(-2147483648, 2147483647)
            imm = random.randint(-100, 100) * 4
            pc_start = 30000 + i * 4

            if rs1 != 0:
                p(f"scoreboard players set #{rs1} {SB} {v1}")

            p(f"scoreboard players set #pc {SB} {pc_start}")

            if name == "jal":
                pc_exp = to_int32(pc_start + imm)
            else:
                target = (v1 if rs1 != 0 else 0) + imm
                pc_exp = to_int32(target & ~1)

            rd_exp = to_int32(pc_start + 4)

            rd_target = "trash_bin" if rd == 0 else str(rd)
            if name == "jal":
                p(f'function {NS}:i_{name} {{rd:"{rd_target}",imm:"{imm}"}}')
            else:
                p(
                    f'function {NS}:i_{name} {{rs1:"{rs1}",rd:"{rd_target}",imm:"{imm}"}}'
                )

            tgt = "trash_bin" if rd == 0 else rd
            obj = SB if rd != 0 else "trash_bin"
            p(
                f"execute unless score #{tgt} {obj} matches {rd_exp} run say FAIL:{name}:rd:exp:{rd_exp} {os.urandom(4).hex()}"
            )
            p(
                f"execute unless score #pc {SB} matches {pc_exp} run say FAIL:{name}:pc:exp:{pc_exp} {os.urandom(4).hex()}"
            )

    p("say Finished.")


if __name__ == "__main__":
    print("function test {")
    gen()
    print("}")
