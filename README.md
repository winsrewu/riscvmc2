# riscvmc2

A tool to compile RISC-V instructions to Minecraft commands.

Now supports U-Mode RV32IM. (No Zicsr, Zifencei, privileged architecture support)

This project is developed under Minecraft 1.21.5, not much tricks are used.
So I think versions around it or upper ones can work too.

## Performance

About **69** commands per instruction.

About 20 KIPS (20k instructions per second), almost as fast as 1960s CPUs.

## Similar Repositories
- https://github.com/winsrewu/riscvmc Generation #1 Emulator. Super Slow.
- https://github.com/SuperTails/riscvcraft Another emulator but with rv32ima. This author also have llvm / wasm support for mc datapack.
- https://github.com/Steve3184/MC-RVVM Another compiler.
- https://github.com/Steve3184/mcrvemu Another emulator.

## Versioning

This project has no need to versioning at the moment.

## Quick Start

Download https://storage.jawbts.org/datapack/eliza%40riscvmc2.zip,
put it into your datapack folder. Recommanded Minecraft version: 1.21.5.

Then, enable the datapack.
Please notice that there's a limit in Minecraft of commands per tick.
You can set it via ``/gamerule maxCommandChainLength <>``.

To summon the terminal, do
``
/summon minecraft:text_display ~ ~ ~ {Tags:["riscvmc2_terminal"], alignment:"left", line_width:400}
``.

To print the keyboard to a player,
do ``/function org_jawbts_riscvmc2_terminal:print_keyboard``
as the player.

To reload, do ``/function org_jawbts_riscvmc2_main:reload``.

To load the datapack, do ``/function org_jawbts_riscvmc2_main:reload``

To run the datapack,
do ``/scoreboard players set #running org_jawbts_riscvmc2 1`` once and
do ``/function org_jawbts_riscvmc2_main:tick1000`` multiple times
(a repeating command block is suggested).

## Not Quick Start

You need [RISC-V GNU Toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain) (May require you 2~3 hours, 16+ GB disk space and Linux, whatever real machine or wsl, to download & compile) to cross compile the target program and [beet](https://github.com/mcbeet/beet) & [mcbuild](https://github.com/mc-build/mcb) (4.0.0 dev version) to build this project.


Set machine architecture (march) to RV32IM and machine application binary interface (mabi) to ilp32.

And check the build scripts in ``app/``

-O3 is used because we have a high look-up speed but low execution speed.

And do ``beet build`` to encode the program into MC functions.
Actually, beet will generate a datapack and install directly into your world.
Check ``compile.py`` for details and ``beet.json`` to change the destination.

It is suggested to use Linux or wsl (project on vhdx) to build,
since they have better performance on small file operations.
You can let beet zip the output and send it to Windows.

For some program which requires a super long boot up, loading form snapshots (or I call it dumps) is recommanded.
Check the dump system call in [reference model](pyriscv/README.md#system-calls-table). You need to spilt the output dump file into two and then check ``plugin/stage_1.py`` and ``plugin/stage_2.py``.

## Techincal Details

### Project Structure

#### Reference Module and Tests

Reference module: ``pyriscv/``.

``test/pc_log_to_mcf.py`` can be used to check whether they have the
same behavior (pc and all registers).

Unfortuately RISC-V's official test kit doesn't like U-mode only emulators.
So we have our own.

#### Memory Structure

The linker script devided the whole memory into two sectors, text (unmodifiable but executable) and data (modifiable but unexecutable).  
All data in the text sector should be vaild instructions, and they will be encoded into a series of function calls. Details will be explained later.
All data in the data sector is stored into scoreboard.

#### Text Storage

We have two options to store the text,
one is storing function names (we generate one function for each type of instruction in this case, we call it standalone) and arguments in Minecraft Storage as string and running via marco.
Another is storing them in Minecraft Function, one function file per vaild instruction.

In the second case, some type of the instruction may be too complicated that inline expand them is not a wise choice, so they will call a standalone one instead. You can set whether to inline expand a type of instruction in the config.

### Build Process

+ Stage 1  
Built-in sources (e.g. standalone instruction implements).  
No cache due to that almost all changes can affect this stage, and it's fast.

+ Stage 2
Custom sources (e.g. the C++ files).  
Cache default to true.


### System Calls Table

Check reference model's [readme](pyriscv/README.md#system-calls-table).

You can check ``app/c-common`` for example.

### Build Config

Check the comments in the config python source code.

### Others

Check the comments in the files.

## Contributing

Before PRs, let me know about it first please.  

This project uses Black Formatter for python code.

## TODO

- [x] ``Execute`` based fast iterations
- [x] M extension
- [ ] Linux in Minecraft
- [ ] ``Execute`` magic based faster bitwise operations & module management
- [ ] Native Minecraft command / function calls based on custom instruction (Something like ``ecall``)
- [ ] Performance
- [x] Reload without ``/reload`` command

## NOT TODO

- Privileged architecture. This will bring extra complexity. Unless you have a elegant and high quality way to implement it.