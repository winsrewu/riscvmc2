from enum import Enum


class OptionalValueEnum(Enum):
    @classmethod
    def from_value(cls, value):
        try:
            return cls(value)
        except ValueError:
            return None


class PyriscvCodeClass(OptionalValueEnum):
    BASE = 0b11


class PyriscvOpCode(OptionalValueEnum):
    LUI = 0b01101
    AUIPC = 0b00101
    JAL = 0b11011
    JALR = 0b11001
    BRANCH = 0b11000
    OP_IMM = 0b00100
    OP = 0b01100
    LOAD = 0b00000
    STORE = 0b01000
    FENCE = 0b00011
    ECALL = 0b11100


class PyriscvFunct3Op(OptionalValueEnum):
    ADD_SUB = 0b000
    SLL = 0b001
    SRL_SRA = 0b101
    SLT = 0b010
    SLTU = 0b011
    XOR = 0b100
    OR = 0b110
    AND = 0b111


class PyriscvFunct3Branch(OptionalValueEnum):
    BEQ = 0b000
    BNE = 0b001
    BLT = 0b100
    BGE = 0b101
    BLTU = 0b110
    BGEU = 0b111


class PyriscvFunct3LoadStore(OptionalValueEnum):
    B = 0b000
    H = 0b001
    W = 0b010
    BU = 0b100
    HU = 0b101


INSTRUCTION_LIST = {
    "I": [
        "add",
        "addi",
        "sub",
        "and",
        "andi",
        "or",
        "ori",
        "xor",
        "xori",
        "sll",
        "slli",
        "sra",
        "srai",
        "srl",
        "srli",
        "lui",
        "auipc",
        "slt",
        "slti",
        "sltu",
        "sltiu",
        "beq",
        "bne",
        "bge",
        "bgeu",
        "blt",
        "bltu",
        "jal",
        "jalr",
        "lw",
        "lh",
        "lhu",
        "lb",
        "lbu",
        "sw",
        "sh",
        "sb",
        "should_not_call",
        "ecall",
    ]
}
