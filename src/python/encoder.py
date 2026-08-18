from .decoder import PyriscvDecodedInstruction
from .pyriscv_definition import *
from .memory_slice import *


def encode_to_function(decoded_inst: PyriscvDecodedInstruction) -> tuple[str, dict]:
    name, arg = _encode_to_function(decoded_inst)

    if "rd" in arg and arg["rd"] == 0:
        arg["rd"] = "trash_bin"
    for k, v in arg.items():
        if isinstance(v, int):
            arg[k] = Operand(v, 32).signed()

    return name, arg


def _encode_to_function(decoded_inst: PyriscvDecodedInstruction) -> tuple[str, dict]:
    if decoded_inst.codeclass != PyriscvCodeClass.BASE:
        raise ValueError("Invalid code class")

    if decoded_inst.opcode == PyriscvOpCode.JAL:
        return "jal", {
            "rd": decoded_inst.rd.unsigned(),
            "imm": decoded_inst.immj.signed(),
        }

    if decoded_inst.opcode == PyriscvOpCode.JALR:
        return "jalr", {
            "rd": decoded_inst.rd.unsigned(),
            "rs1": decoded_inst.rs1.unsigned(),
            "imm": decoded_inst.immi.signed(),
        }

    if decoded_inst.opcode == PyriscvOpCode.BRANCH:
        name = None
        if decoded_inst.funct3branch == PyriscvFunct3Branch.BEQ:
            name = "beq"
        if decoded_inst.funct3branch == PyriscvFunct3Branch.BNE:
            name = "bne"
        if decoded_inst.funct3branch == PyriscvFunct3Branch.BGE:
            name = "bge"
        if decoded_inst.funct3branch == PyriscvFunct3Branch.BGEU:
            name = "bgeu"
        if decoded_inst.funct3branch == PyriscvFunct3Branch.BLT:
            name = "blt"
        if decoded_inst.funct3branch == PyriscvFunct3Branch.BLTU:
            name = "bltu"
        if name is None:
            raise ValueError("Invalid branch funct3")

        return name, {
            "rs1": decoded_inst.rs1.unsigned(),
            "rs2": decoded_inst.rs2.unsigned(),
            "imm": decoded_inst.immb.signed(),
        }

    if decoded_inst.opcode == PyriscvOpCode.OP_IMM:
        name = None
        if decoded_inst.funct3op == PyriscvFunct3Op.ADD_SUB:
            name = "addi"
        if decoded_inst.funct3op == PyriscvFunct3Op.AND:
            name = "andi"
        if decoded_inst.funct3op == PyriscvFunct3Op.OR:
            name = "ori"
        if decoded_inst.funct3op == PyriscvFunct3Op.XOR:
            name = "xori"
        if decoded_inst.funct3op == PyriscvFunct3Op.SLL:
            name = "slli"
        if decoded_inst.funct3op == PyriscvFunct3Op.SRL_SRA:
            if int(decoded_inst.funct7) == 0x00:
                name = "srli"
            elif int(decoded_inst.funct7) == 0x20:
                name = "srai"
            else:
                raise ValueError("Invalid funct7 for srli/srai")
        if decoded_inst.funct3op == PyriscvFunct3Op.SLT:
            name = "slti"
        if decoded_inst.funct3op == PyriscvFunct3Op.SLTU:
            name = "sltiu"
        if name is None:
            raise ValueError("Invalid op_imm funct3")

        return name, {
            "rd": decoded_inst.rd.unsigned(),
            "rs1": decoded_inst.rs1.unsigned(),
            "imm": decoded_inst.immi.signed(),
        }

    if decoded_inst.opcode == PyriscvOpCode.OP:
        name = None
        if int(decoded_inst.funct7) == 0x01:
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.MUL:
                name = "mul"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.MULH:
                name = "mulh"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.MULHU:
                name = "mulhu"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.MULHSU:
                name = "mulhsu"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.DIV:
                name = "div"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.DIVU:
                name = "divu"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.REM:
                name = "rem"
            if decoded_inst.funct3opmul == PyriscvFunct3OpMul.REMU:
                name = "remu"
        else:
            if decoded_inst.funct3op == PyriscvFunct3Op.ADD_SUB:
                if int(decoded_inst.funct7) == 0x00:
                    name = "add"
                elif int(decoded_inst.funct7) == 0x20:
                    name = "sub"
                else:
                    raise ValueError("Invalid funct7 for add/sub")
            if decoded_inst.funct3op == PyriscvFunct3Op.AND:
                name = "and"
            if decoded_inst.funct3op == PyriscvFunct3Op.OR:
                name = "or"
            if decoded_inst.funct3op == PyriscvFunct3Op.XOR:
                name = "xor"
            if decoded_inst.funct3op == PyriscvFunct3Op.SLL:
                name = "sll"
            if decoded_inst.funct3op == PyriscvFunct3Op.SRL_SRA:
                if int(decoded_inst.funct7) == 0x00:
                    name = "srl"
                elif int(decoded_inst.funct7) == 0x20:
                    name = "sra"
                else:
                    raise ValueError("Invalid funct7 for srl/sra")
            if decoded_inst.funct3op == PyriscvFunct3Op.SLT:
                name = "slt"
            if decoded_inst.funct3op == PyriscvFunct3Op.SLTU:
                name = "sltu"
        if name is None:
            raise ValueError("Invalid op_imm funct3")

        return name, {
            "rd": decoded_inst.rd.unsigned(),
            "rs1": decoded_inst.rs1.unsigned(),
            "rs2": decoded_inst.rs2.unsigned(),
        }

    if decoded_inst.opcode == PyriscvOpCode.LUI:
        return "lui", {
            "rd": decoded_inst.rd.unsigned(),
            "imm": decoded_inst.immu.unsigned(),
        }

    if decoded_inst.opcode == PyriscvOpCode.AUIPC:
        return "auipc", {
            "rd": decoded_inst.rd.unsigned(),
            "imm": decoded_inst.immu.unsigned(),
        }

    if decoded_inst.opcode == PyriscvOpCode.LOAD:
        name = None
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.W:
            name = "lw"
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.H:
            name = "lh"
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.HU:
            name = "lhu"
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.B:
            name = "lb"
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.BU:
            name = "lbu"
        if name is None:
            raise ValueError("Invalid load funct3")

        return name, {
            "rd": decoded_inst.rd.unsigned(),
            "rs1": decoded_inst.rs1.unsigned(),
            "imm": decoded_inst.immi.signed(),
        }

    if decoded_inst.opcode == PyriscvOpCode.STORE:
        name = None
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.W:
            name = "sw"
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.H:
            name = "sh"
        if decoded_inst.funct3loadstore == PyriscvFunct3LoadStore.B:
            name = "sb"
        if name is None:
            raise ValueError("Invalid store funct3")

        return name, {
            "rs1": decoded_inst.rs1.unsigned(),
            "rs2": decoded_inst.rs2.unsigned(),
            "imm": decoded_inst.imms.signed(),
        }

    if Operand(decoded_inst.raw_instruction).unsigned() == 0x00000073:
        return "ecall", {}

    # There's a hardcoded csr instruction in std c lib, for exception handling
    # But we doesn't support it.
    if Operand(decoded_inst.raw_instruction).unsigned() == 0xC2202573:  # csrrs a0, zero
        return "should_not_call", {}
    
    # Another stuff found in _start, mysterious hardcoded instruction
    if Operand(decoded_inst.raw_instruction).unsigned() == 0x1751073: # csrw jvt, a0
        return "should_bypass", {}

    raise ValueError("Invalid instruction")


def encode_to_scoreboard(data_dict: dict):
    for addr, data in sorted(data_dict.items(), key=lambda x: x[0]):
        yield f"scoreboard players set #{Operand(addr).signed()} org_jawbts_riscvmc2_memory {Operand(data).signed()}"
