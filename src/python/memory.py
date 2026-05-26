from .memory_slice import MemorySlice32, Operand


def default_keep_text_section(addr):
    return addr >= 0 and addr < 0x20000000


def default_keep_data_section(addr):
    return not default_keep_text_section(addr)


def read_verilog_v8(filename: str, keep: callable):
    memory = {}
    with open(filename, "r") as f:
        addr = 0
        for line in f.readlines():
            segs = line.strip().split(" ")
            for seg in segs:
                if seg == "":
                    continue
                if seg.startswith("@"):
                    addr = int(seg[1:], 16)
                else:
                    data = int(seg, 16)
                    if keep(addr):
                        memory[addr] = data
                    addr += 1
    return memory


def process_memory_into_raw_inst(memory: dict):
    count = len(memory.keys())
    for addr, data in memory.items():
        if addr % 4 != 0:
            continue
        if not (
            addr + 1 in memory.keys()
            and addr + 2 in memory.keys()
            and addr + 3 in memory.keys()
        ):
            raise Exception("Invalid instruction at address 0x%x" % addr)
        inst = (
            (memory[addr + 3] << 24)
            | (memory[addr + 2] << 16)
            | (memory[addr + 1] << 8)
            | memory[addr]
        )
        count -= 4
        yield MemorySlice32(inst), Operand(addr)
    if count != 0:
        raise Exception("Invalid memory")


def process_memory_into_data(memory: dict):
    data_dict = {}
    for addr, data in memory.items():
        target_addr = addr & ~0b11
        target_shift = 8 * (addr & 0b11)
        data_dict[target_addr] = data_dict.get(target_addr, 0) | (data << target_shift)
    return data_dict
