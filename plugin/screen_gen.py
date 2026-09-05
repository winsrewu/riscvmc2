"""screen_gen -- generate the standardized screen (single draw ecall 2000).

Single draw-call ABI, shared with the pyriscv reference (keep in sync):
  * screen geometry: PyriscvConfig screen_width x screen_height (default
    192 x 168), row-major, origin at the top-left.  See pyriscv
    src/pyscreen.py and app/gfx-saver/main.c.
  * the guest framebuffer is int[screen_width * screen_height] words at
    the fixed base _screen_fb -- see pyriscv app/c-common/link.ld
    (SCREENFB region, currently 0x30000000).  One word per pixel:
    0 = black, else white.
  * wall placement and orientation are build-time config
    (PyriscvConfig.screen_origin / screen_facing / screen_top): pixel
    (gx, gy) maps to world origin + gx * column + gy * row, gy = 0 being
    the TOP row.  Vertical walls (facing north/south/east/west) lay rows
    downward, columns as seen from the front; the defaults reproduce the
    classic wall at x 0..191, y 64..231, z = 0.  Horizontal screens
    (facing up/down, i.e. a floor or a ceiling) lie flat with the content
    top pointing at screen_top.

All of these are PyriscvConfig fields; when changing one, see the "keep
in sync" list in src/python/config.py (which places must change on the
pyriscv guest side too).

Every pixel word lives in the guest-memory scoreboard
(org_jawbts_riscvmc2_memory, player name "#<addr>").  The MC side keeps a
per-pixel cache in org_jawbts_riscvmc2_screen_cache with the SAME player
names; a draw only rewrites blocks whose value differs from the cache, so
unchanged pixels never hit setblock (setblock is the expensive part).

IMPORTANT: in Minecraft a player WITHOUT a scoreboard entry does not match
any `matches` range and never equals another player, so the per-pixel color
tests below only use explicit ranges (`matches 0` for black, `1..` and
`..-1` for white) -- never `unless ... matches 0`, which would treat an
unwritten pixel as white.  Unwritten pixels simply keep the wall colour
(the wall is painted black by init), which is what "0 = black" means.

When PyriscvConfig.screen_enabled is False nothing of the above is
generated: only no-op ecall handlers keep the dispatch valid, no
minecraft:tick registration happens and init is skipped by reload (see
the IF (config.screenEnabled) in org_jawbts_riscvmc2_main).

Generated functions (added to ctx.data.functions every build):
  org_jawbts_riscvmc2_screen:draw      -- ecall 2000 handler target
  org_jawbts_riscvmc2_screen:init      -- reset objectives + black wall
  org_jawbts_riscvmc2_screen:draw_NN   -- static per-pixel compare chunks
  org_jawbts_riscvmc2_screen:init_NN   -- memory pre-fill chunks
  org_jawbts_riscvmc2_screen:tick_gt   -- game tick clock (ecall 2001)
  org_jawbts_riscvmc2_screen:gt_wait   -- blocking wait (ecall 2002)
  org_jawbts_riscvmc2_screen:key_get   -- key lookup (ecall 2003)
  org_jawbts_riscvmc2_screen:key_reset -- clear all latched keys
"""

from beet import Context, Function, FunctionTag

# ---- ABI constants (keep in sync with pyriscv) ----------------------
# Screen size comes from PyriscvConfig (screen_width / screen_height);
# only the fixed fb base lives here.
FB_BASE = 0x30000000  # _screen_fb in pyriscv app/c-common/link.ld

NS = "org_jawbts_riscvmc2_screen"
MEM_OBJ = "org_jawbts_riscvmc2_memory"
CACHE_OBJ = "org_jawbts_riscvmc2_screen_cache"
KEY_OBJ = "org_jawbts_riscvmc2_key"
REG_OBJ = "org_jawbts_riscvmc2_register"
CTRL_OBJ = "org_jawbts_riscvmc2"          # #running / #ecall_block
TEMP_OBJ = "org_jawbts_riscvmc2_temp"      # #game_gt and scratch flags

# game tick clock (ecall 2001/2002): 1 game tick = 1/20 s = 1 MC tick
GT_COUNTER = "#game_gt"
GT_WAIT_FLAG = "#scr_gw"
GT_WAIT_TGT = "#scr_gw_tgt"

# keys (ecall 2003): guest reads #k_<n>; the operator sets them manually,
# e.g. /scoreboard players set #k_0 org_jawbts_riscvmc2_key 1.  They are
# latched until the next SCR_DRAW, which resets all of them.
KEY_COUNT = 32

BLACK_BLOCK = "minecraft:black_concrete"
WHITE_BLOCK = "minecraft:white_concrete"

# line budget per generated file, so no single function is gigantic
CHUNK_LINES = 6000

# Screen facing: compass/axis direction the front (painted side) points,
# i.e. where the viewer stands.  Vertical walls (fy == 0) have their
# content top pointing world-up; horizontal screens (facing up/down) lie
# flat and use screen_top (a compass point) as the direction the content
# top edge points at.
_FACING_VEC = {
    "south": (0, 0, 1),
    "north": (0, 0, -1),
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
    "up": (0, 1, 0),     # floor, seen from above
    "down": (0, -1, 0),  # ceiling, seen from below
}
_COMPASS_VEC = {
    "south": (0, 0, 1),
    "north": (0, 0, -1),
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
}
_UP = (0, 1, 0)


def _cross(a, b):
    ax, ay, az = a
    bx, by, bz = b
    return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)


def _neg(v):
    return tuple(-x for x in v)


def _axes(config):
    """Return (column step for gx + 1, row step for gy + 1).

    The viewer gazes toward -facing; the layout reads un-mirrored from
    that side.  Vertical walls: rows run straight down, columns run to
    the viewer's right.  Horizontal screens: rows run from the top edge
    (screen_top) to the opposite side, columns to the viewer's right
    when standing on that opposite side.
    """
    facing = _FACING_VEC[config.screen_facing]
    if facing[1] == 0:  # vertical wall
        row = (0, -1, 0)
        col = _cross(_neg(facing), _UP)
    else:  # horizontal screen: screen_top picks the content-top direction
        row = _neg(_COMPASS_VEC[config.screen_top])
        col = _cross(_neg(row), _UP)
    return col, row


def _pixels(config):
    """Yield (player_name, block_x, block_y, block_z), row-major."""
    ox, oy, oz = config.screen_origin
    w, h = config.screen_width, config.screen_height
    (cx, cy, cz), (rx, ry, rz) = _axes(config)
    for i in range(w * h):
        addr = FB_BASE + 4 * i
        gx = i % w
        gy = i // w
        yield (
            f"#{addr}",
            ox + gx * cx + gy * rx,
            oy + gx * cy + gy * ry,
            oz + gx * cz + gy * rz,
        )


def _wall_box(config):
    """Axis-aligned block box covering the whole wall (init black fill)."""
    ox, oy, oz = config.screen_origin
    w, h = config.screen_width, config.screen_height
    (cx, cy, cz), (rx, ry, rz) = _axes(config)
    xs = [
        ox + gx * cx + gy * rx
        for gx in (0, w - 1)
        for gy in (0, h - 1)
    ]
    ys = [
        oy + gx * cy + gy * ry
        for gx in (0, w - 1)
        for gy in (0, h - 1)
    ]
    zs = [
        oz + gx * cz + gy * rz
        for gx in (0, w - 1)
        for gy in (0, h - 1)
    ]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def _chunks(lines):
    for start in range(0, len(lines), CHUNK_LINES):
        yield lines[start : start + CHUNK_LINES]


def generate_screen(ctx: Context, config):
    funcs = ctx.data.functions

    if not config.screen_enabled:
        # Screen built out (see config.py).  Keep the ecall dispatch
        # (rv32i.mcb) valid with no-op handlers that just release the
        # cpu; nothing else is generated -- no minecraft:tick entry, no
        # init (reload skips it as well).  A screen guest on such a build
        # gets black, no clock and no keys instead of an error.
        release = f"scoreboard players set #ecall_block {CTRL_OBJ} 0"
        funcs[f"{NS}:draw"] = Function([release])
        funcs[f"{NS}:gt_wait"] = Function([release])
        funcs[f"{NS}:key_get"] = Function(
            [
                f"scoreboard players set #10 {REG_OBJ} 0",
                release,
            ]
        )
        return

    # ---- per-pixel compare/setblock chunks ---------------------------
    draw_lines = []
    for name, bx, by, bz in _pixels(config):
        pos = f"{bx} {by} {bz}"
        neq = f"unless score {name} {MEM_OBJ} = {name} {CACHE_OBJ}"
        # Explicit value ranges only (see module docstring): an unwritten
        # pixel matches nothing, so it is left alone and keeps the black
        # wall from init.
        draw_lines.append(
            f"execute {neq} if score {name} {MEM_OBJ} matches 0 "
            f"run setblock {pos} {BLACK_BLOCK}"
        )
        draw_lines.append(
            f"execute {neq} unless score {name} {MEM_OBJ} matches 0 "
            f"run setblock {pos} {WHITE_BLOCK}"
        )
        draw_lines.append(
            f"scoreboard players operation {name} {CACHE_OBJ} = {name} {MEM_OBJ}"
        )

    draw_chunk_ids = []
    for i, chunk in enumerate(_chunks(draw_lines)):
        fid = f"{NS}:draw_{i:02d}"
        funcs[fid] = Function(chunk)
        draw_chunk_ids.append(fid)

    # pre-fill memory region to avoid None
    init_chunk_ids = []
    n_px = config.screen_width * config.screen_height
    for i, chunk in enumerate(
        _chunks(
            [
                f"scoreboard players set #{FB_BASE + 4 * i} {MEM_OBJ} 0"
                for i in range(n_px)
            ]
        )
    ):
        fid = f"{NS}:init_{i:02d}"
        funcs[fid] = Function(chunk)
        init_chunk_ids.append(fid)

    funcs[f"{NS}:draw"] = Function(
        [f"function {fid}" for fid in draw_chunk_ids]
        + [f"function {NS}:key_reset"]  # frame done -> clear all key flags
    )

    # ---- game tick clock (ecall 2001/2002) --------------------------

    funcs[f"{NS}:tick_gt"] = Function(
        [f"scoreboard players add {GT_COUNTER} {TEMP_OBJ} 1"]
    )
    # Runs once per MC tick, giving the guest a stable 1/20 s clock.
    # The tick tag may already exist (mcbuild sources register their own
    # `function tick minecraft:tick` entries).  Its content -- whether a
    # FunctionTag or a raw dict -- is a {"values": [...]} mapping.
    tick_tag = ctx.data.function_tags.setdefault(
        "minecraft:tick", FunctionTag()
    )
    if isinstance(tick_tag, dict):
        values = tick_tag.setdefault("values", [])
    else:
        values = tick_tag.data.setdefault("values", [])
    if f"{NS}:tick_gt" not in values:
        values.append(f"{NS}:tick_gt")

    # Blocking wait: called from the ecall dispatch while #ecall_block is
    # still 1.  Captures the target tick on entry, then on every retry
    # (one per instruction step, many per MC tick) releases the CPU once
    # the tick counter has moved past it.
    funcs[f"{NS}:gt_wait"] = Function(
        [
            f"execute if score {GT_WAIT_FLAG} {TEMP_OBJ} matches 0 "
            f"run scoreboard players operation {GT_WAIT_TGT} {TEMP_OBJ} "
            f"= {GT_COUNTER} {TEMP_OBJ}",
            f"execute if score {GT_WAIT_FLAG} {TEMP_OBJ} matches 0 "
            f"run scoreboard players add {GT_WAIT_TGT} {TEMP_OBJ} 1",
            f"scoreboard players set {GT_WAIT_FLAG} {TEMP_OBJ} 1",
            f"execute if score {GT_COUNTER} {TEMP_OBJ} >= "
            f"{GT_WAIT_TGT} {TEMP_OBJ} run scoreboard players set "
            f"{GT_WAIT_FLAG} {TEMP_OBJ} 0",
            f"execute if score {GT_COUNTER} {TEMP_OBJ} >= "
            f"{GT_WAIT_TGT} {TEMP_OBJ} run scoreboard players set "
            f"#ecall_block {CTRL_OBJ} 0",
        ]
    )

    # ---- keys (ecall 2003) ------------------------------------------

    funcs[f"{NS}:key_reset"] = Function(
        [
            f"scoreboard players set #k_{n} {KEY_OBJ} 0"
            for n in range(KEY_COUNT)
        ]
    )

    key_get_lines = [
        f"scoreboard players operation #scr_key {TEMP_OBJ} = "
        f"#10 {REG_OBJ}",
        f"scoreboard players set #10 {REG_OBJ} 0",
    ]
    for n in range(KEY_COUNT):
        key_get_lines.append(
            f"execute if score #scr_key {TEMP_OBJ} matches {n} run "
            f"scoreboard players operation #10 {REG_OBJ} = "
            f"#k_{n} {KEY_OBJ}"
        )
    funcs[f"{NS}:key_get"] = Function(key_get_lines)

    x0, y0, z0, x1, y1, z1 = _wall_box(config)
    funcs[f"{NS}:init"] = Function(
        [
            f"scoreboard objectives remove {CACHE_OBJ}",
            f"scoreboard objectives add {CACHE_OBJ} dummy",
            f"scoreboard objectives remove {KEY_OBJ}",
            f"scoreboard objectives add {KEY_OBJ} dummy",
            f"scoreboard players set {GT_COUNTER} {TEMP_OBJ} 0",
            f"scoreboard players set {GT_WAIT_FLAG} {TEMP_OBJ} 0",
            f"fill {x0} {y0} {z0} {x1} {y1} {z1} "
            f"minecraft:black_concrete",
        ]
        + [f"function {fid}" for fid in init_chunk_ids]
        + [f"function {NS}:key_reset"]
    )
