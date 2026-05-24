from pyriscv_definition import *
from memory_slice import *

class PyriscvDecodedInstruction():
    raw_instruction: MemorySlice32
    codeclass: PyriscvCodeClass | None
    opcode: PyriscvOpCode | None
    funct3op: PyriscvFunct3Op | None
    funct3branch: PyriscvFunct3Branch | None
    funct3loadstore: PyriscvFunct3LoadStore | None
    funct7: Operand
    rs1: Operand
    rs2: Operand
    rd: Operand
    immi: Operand
    imms: Operand
    immb: Operand
    immu: Operand
    immj: Operand

    def __init__(self, raw_instruction: MemorySlice32):
        self.raw_instruction = raw_instruction
        self.codeclass = PyriscvCodeClass.from_value(raw_instruction[1:0])
        self.opcode = PyriscvOpCode.from_value(raw_instruction[6:2])
        self.funct3op = PyriscvFunct3Op.from_value(raw_instruction[14:12])
        self.funct3branch = PyriscvFunct3Branch.from_value(raw_instruction[14:12])
        self.funct3loadstore = PyriscvFunct3LoadStore.from_value(raw_instruction[14:12])
        self.funct7 = Operand(raw_instruction[31:25], 7)
        self.rs1 = Operand(raw_instruction[20:15], 5)
        self.rs2 = Operand(raw_instruction[25:20], 5)
        self.rd = Operand(raw_instruction[11:7], 5)
        self.immi = Operand(raw_instruction[31:20], 12)
        self.imms = Operand(raw_instruction[31:25] << 5 | raw_instruction[11:7], 12)
        self.immb = Operand(raw_instruction[31] << 12 | raw_instruction[7] << 11 | raw_instruction[30:25] << 5
                            | raw_instruction[11:8] << 1, 13)
        self.immu = Operand(raw_instruction[31:12] << 12, 32)
        self.immj = Operand(raw_instruction[31] << 20 | raw_instruction[19:12] << 12
                            | raw_instruction[20] << 11 | raw_instruction[30:21] << 1, 21)