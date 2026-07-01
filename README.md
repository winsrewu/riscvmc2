# riscvmc2

A tool to compile RISC-V instructions to Minecraft commands.

Now supports U-Mode RV32I. (No Zicsr, Zifencei, privileged architecture support)

This project is developed under Minecraft 1.21.5, not much tricks are used.
So I think versions around it or upper ones can work too.

## Performance

About **69** commands per instruction.

## Similar Repositories
- https://github.com/winsrewu/riscvmc Generation #1 Emulator. Super Slow.
- https://github.com/SuperTails/riscvcraft Another emulator but with rv32ima. This author also have llvm / wasm support for mc datapack.
- https://github.com/Steve3184/MC-RVVM Another compiler.
- https://github.com/Steve3184/mcrvemu Another emulator.

## Versioning

This project has no need to versioning at the moment.

## Quick Start

*Working On It*

## Not Quick Start

You need [RISC-V GNU Toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain) (May require you 2~3 hours, 16+ GB disk space and Linux, whatever real machine or wsl, to download & compile) to cross compile the target program and [beet](https://github.com/mcbeet/beet) & [mcbuild](https://github.com/mc-build/mcb) (4.0.0 dev version) to build this project.


Set machine architecture (march) to RV32I and machine application binary interface (mabi) to ilp32.

And check the build scripts in ``app/``

-O3 is used because we have a high look-up speed but low execution speed.

And do ``beet build`` to encode the program into MC functions.
Actually, beet will generate a datapack and install directly into your world.
Check ``compile.py`` for details and ``beet.json`` to change the destination.

For some program which requires a super long boot up, loading form snapshots (or I call it dumps) is recommanded.
Check the dump system call in https://github.com/winsrewu/pyriscv. You need to spilt the output dump file into two and then check ``plugin/loader.py``.

## Techincal Details

### Project Structure

The linker script devided the whole memory into two sectors, text (unmodifiable but executable) and data (modifiable but unexecutable).  
All data in the text sector should be vaild instructions, and they will be encoded into a series of function calls. We have one function for every instruction.  
All data in the data sector is stored into scoreboard.

This project has a reference model, https://github.com/winsrewu/pyriscv,
a python emulator. We have tests there, and tests here.

### System Calls Table

| number | function | args | return |
|--------|----------|------|--------|
| 63     | read     | fd, ptr, len | number of bytes read |
| 64     | write    | fd, ptr, len | number of bytes written |
| 93     | exit     | error_code | - |

You can check ``app/c-common`` for example.

### Others

Check the comments in the files.

## Contributing

Before PRs, let me know about it first please.  

This project uses Black Formatter for python code.

## TODO

- [ ] ``Execute`` based fast iterations
- [ ] M extension
- [ ] Linux in Minecraft
- [ ] ``Execute`` magic based faster bitwise operations & module management
- [ ] Native Minecraft command / function calls based on custom instruction (Something like ``ecall``)
- [ ] Performance
- [ ] Reload without ``/reload`` command

## NOT TODO

- Privileged architecture. This will bring extra complexity. Unless you have a elegant and high quality way to implement it.