// Screen library data for riscvmc2 — transcribed 1:1 from
// pyriscv's src/pygfx.py (which mirrors app/minecraft-1960-c/render.c).

// Block ids (mc.h)
const B_AIR = 0;
const B_GRASS = 1, B_DIRT = 2, B_STONE = 3, B_COBBLE = 4, B_BEDROCK = 5;
const B_LOG = 6, B_LEAVES = 7, B_PLANKS = 8, B_CRAFT = 9, B_FURNACE = 10;
const B_SAND = 11, B_GRAVEL = 12, B_COAL = 13, B_IRON = 14, B_DIAMOND = 15;
const B_WATER = 16, B_LAVA = 17, B_OBSIDIAN = 18, B_PORTAL = 19;
const B_NETHERRACK = 20, B_NBRICK = 21, B_SPAWNER = 22, B_ENDSTONE = 23;
const B_SBRICK = 24, B_FRAME = 25, B_FRAME_EYE = 26, B_ENDPORTAL = 27;

const I_STICK = 40, I_COAL = 41, I_FLINT = 42, I_IRONING = 43, I_DIAMOND = 44;
const I_BUCKET = 45, I_BUCKET_W = 46, I_BUCKET_L = 47, I_FSTEEL = 48, I_ROD = 49;
const I_POWDER = 50, I_PEARL = 51, I_EYE = 52;
const I_WPICK = 53, I_WAXE = 54, I_WSWORD = 55;
const I_SPICK = 56, I_SAXE = 57, I_SSWORD = 58;
const I_IPICK = 59, I_IAXE = 60, I_ISWORD = 61;
const I_DPICK = 62, I_DAXE = 63, I_DSWORD = 64;

// solid_r: is the block solid (0 for air/water/lava/portal/endportal)
const SOLID = [
  0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0,
];

// 3x5 font, 48 glyphs x 5 rows (same order as render.c)
const FONT = [
  7, 5, 5, 5, 7,    // 0
  2, 6, 2, 2, 7,    // 1
  6, 1, 2, 4, 7,    // 2
  6, 1, 2, 1, 6,    // 3
  5, 5, 7, 1, 1,    // 4
  7, 4, 6, 1, 6,    // 5
  3, 4, 7, 5, 7,    // 6
  7, 1, 2, 2, 2,    // 7
  7, 5, 7, 5, 7,    // 8
  7, 5, 7, 1, 6,    // 9
  2, 5, 7, 5, 5,    // A
  6, 5, 6, 5, 6,    // B
  3, 4, 4, 4, 3,    // C
  6, 5, 5, 5, 6,    // D
  7, 4, 6, 4, 7,    // E
  7, 4, 6, 4, 4,    // F
  3, 4, 5, 5, 3,    // G
  5, 5, 7, 5, 5,    // H
  7, 2, 2, 2, 7,    // I
  1, 1, 1, 5, 2,    // J
  5, 5, 6, 5, 5,    // K
  4, 4, 4, 4, 7,    // L
  5, 7, 7, 5, 5,    // M
  6, 5, 5, 5, 5,    // N
  2, 5, 5, 5, 2,    // O
  6, 5, 6, 4, 4,    // P
  2, 5, 5, 6, 1,    // Q
  6, 5, 6, 5, 5,    // R
  3, 4, 2, 1, 6,    // S
  7, 2, 2, 2, 2,    // T
  5, 5, 5, 5, 7,    // U
  5, 5, 5, 5, 2,    // V
  5, 5, 7, 7, 5,    // W
  5, 5, 2, 5, 5,    // X
  5, 5, 2, 2, 2,    // Y
  7, 1, 2, 4, 7,    // Z
  0, 0, 0, 0, 0,    // space
  0, 0, 0, 0, 2,    // .
  0, 2, 0, 2, 0,    // :
  2, 2, 2, 0, 2,    // !
  6, 1, 2, 0, 2,    // ?
  0, 0, 7, 0, 0,    // -
  0, 2, 7, 2, 0,    // +
  4, 2, 1, 2, 4,    // >
  1, 2, 4, 2, 1,    // <
  1, 1, 2, 4, 4,    // /
  2, 2, 0, 0, 0,    // '
  0, 0, 0, 2, 4,    // ,
];

function glyph_of(c) {
  const o = c.charCodeAt(0);
  if (o >= 48 && o <= 57) return o - 48;
  if (o >= 65 && o <= 90) return o - 65 + 10;
  if (o >= 97 && o <= 122) return o - 97 + 10;
  if (c === ".") return 37;
  if (c === ":") return 38;
  if (c === "!") return 39;
  if (c === "?") return 40;
  if (c === "-") return 41;
  if (c === "+") return 42;
  if (c === ">") return 43;
  if (c === "<") return 44;
  if (c === "/") return 45;
  if (c === "'") return 46;
  if (c === ",") return 47;
  return 36;
}

// Sprite primitives.  Each returns a list of [dx, dy] pixels relative to
// the icon origin.  dx grows right, dy grows DOWN in game space (the mcb
// layer flips dy when it emits the setblock).
function px(dx, dy) { return [dx, dy]; }
function h(dx0, dx1, dy) {
  const r = [];
  for (let x = dx0; x <= dx1; x++) r.push([x, dy]);
  return r;
}
function v(dx, dy0, dy1) {
  const r = [];
  for (let y = dy0; y <= dy1; y++) r.push([dx, y]);
  return r;
}
function rect(dx, dy, w, hh) {
  return [].concat(h(dx, dx + w - 1, dy), h(dx, dx + w - 1, dy + hh - 1),
                  v(dx, dy + 1, dy + hh - 2), v(dx + w - 1, dy + 1, dy + hh - 2));
}

function tool_kind(id) { return (id - I_WPICK) % 3; }
function tool_tier(id) { return Math.floor((id - I_WPICK) / 3) + 1; }

// Item / block icon sprites (from render.c icon()).
const ICON = {
  [B_GRASS]: rect(1, 1, 6, 6).concat([px(2, 0)], [px(4, 0)], [px(6, 0)], [px(3, 4)], [px(5, 5)]),
  [B_DIRT]: rect(1, 1, 6, 6).concat([px(3, 3)], [px(5, 4)], [px(2, 5)]),
  [B_STONE]: rect(1, 1, 6, 6).concat([px(3, 3)], [px(5, 3)], [px(4, 5)]),
  [B_COBBLE]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 2)], [px(3, 4)], [px(5, 5)]),
  [B_LOG]: v(2, 1, 6).concat(v(5, 1, 6), h(2, 5, 0), h(2, 5, 7)),
  [B_LEAVES]: [px(1, 1), px(4, 2), px(6, 1), px(2, 4), px(5, 5), px(3, 6)],
  [B_PLANKS]: rect(1, 1, 6, 6).concat([px(2, 3)], [px(4, 3)], [px(6, 3)], [px(1, 5)], [px(3, 5)], [px(5, 5)]),
  [B_CRAFT]: rect(1, 2, 6, 5).concat(h(1, 6, 1), [px(3, 4)], [px(4, 4)], [px(2, 5)], [px(5, 5)]),
  [B_FURNACE]: rect(1, 1, 6, 6).concat(h(3, 5, 4), [px(3, 5)], [px(5, 5)]),
  [B_SAND]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 3)], [px(3, 5)]),
  [B_GRAVEL]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 2)], [px(3, 4)], [px(2, 5)], [px(5, 5)]),
  [B_COAL]: rect(1, 1, 6, 6).concat([px(3, 3)], [px(4, 3)], [px(3, 4)], [px(4, 4)]),
  [B_IRON]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 3)], [px(3, 5)], [px(5, 5)]),
  [B_DIAMOND]: rect(1, 1, 6, 6).concat([px(4, 2)], [px(3, 3)], [px(5, 3)], [px(4, 4)]),
  [B_OBSIDIAN]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(3, 3)], [px(4, 4)], [px(5, 5)], [px(5, 2)], [px(2, 5)]),
  [B_NETHERRACK]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 3)], [px(3, 5)]),
  [B_NBRICK]: rect(1, 1, 6, 6).concat(h(1, 6, 4), v(3, 1, 3), v(5, 5, 6)),
  [B_SBRICK]: rect(1, 1, 6, 6).concat(h(1, 6, 4), v(3, 1, 3), v(5, 5, 6)),
  [B_ENDSTONE]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 2)], [px(3, 4)], [px(5, 5)]),
  [B_BEDROCK]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 2)], [px(3, 3)], [px(2, 5)], [px(5, 5)], [px(4, 6)]),
  [I_STICK]: [px(2, 6), px(3, 5), px(4, 4), px(5, 3), px(6, 2)],
  [I_COAL]: [px(3, 3), px(4, 3), px(3, 4), px(4, 4), px(5, 5)],
  [I_FLINT]: [px(4, 2), px(3, 3), px(4, 3), px(5, 3), px(2, 4), px(3, 4), px(4, 4), px(3, 5)],
  [I_IRONING]: rect(1, 3, 6, 3).concat([px(3, 4)], [px(4, 4)]),
  [I_DIAMOND]: [px(3, 1), px(4, 1), px(2, 2), px(5, 2), px(1, 3), px(6, 3), px(2, 4), px(5, 4), px(3, 5), px(4, 5)],
  [I_BUCKET]: h(2, 5, 2).concat(v(2, 3, 6), v(5, 3, 6), h(2, 5, 6), [px(3, 1)], [px(4, 1)]),
  [I_BUCKET_W]: null, // filled below (I_BUCKET + 2 px)
  [I_BUCKET_L]: null, // filled below (I_BUCKET + 4 px)
  [I_FSTEEL]: [px(2, 2), px(2, 3), px(2, 4), px(3, 5), px(4, 5), px(4, 4), px(6, 2), px(5, 1)],
  [I_ROD]: v(4, 2, 6).concat([px(3, 1)], [px(5, 1)], [px(4, 0)]),
  [I_POWDER]: [px(2, 5), px(4, 5), px(6, 5), px(3, 6), px(5, 6), px(3, 3)],
  [I_PEARL]: [px(3, 1), px(4, 1), px(2, 2), px(5, 2), px(1, 3), px(1, 4), px(6, 3), px(6, 4), px(2, 5), px(5, 5), px(3, 6), px(4, 6), px(4, 4)],
  [I_EYE]: [px(3, 1), px(4, 1), px(2, 2), px(5, 2), px(1, 3), px(1, 4), px(6, 3), px(6, 4), px(2, 5), px(5, 5), px(3, 6), px(4, 6), px(3, 3), px(4, 3), px(3, 4), px(4, 4)],
};

ICON[I_BUCKET_W] = ICON[I_BUCKET].concat([px(3, 4)], [px(4, 5)]);
ICON[I_BUCKET_L] = ICON[I_BUCKET].concat([px(3, 4)], [px(4, 4)], [px(3, 5)], [px(4, 5)]);

// Tool sprites (pick / axe / sword), parameterised by id.
function tool_sprite(id) {
  const t = tool_kind(id);
  let base;
  if (t === 0) { // pickaxe
    base = [px(1, 3), px(2, 2), px(3, 1), px(4, 1), px(5, 1), px(6, 2), px(6, 3), px(3, 3), px(3, 4), px(2, 5), px(1, 6)];
  } else if (t === 1) { // axe
    base = [px(2, 1), px(3, 1), px(4, 1), px(2, 2), px(3, 2), px(4, 2), px(2, 3), px(3, 3), px(4, 4), px(3, 5), px(2, 6)];
  } else { // sword
    base = [px(6, 1), px(5, 2), px(4, 3), px(3, 4), px(2, 3), px(4, 5), px(1, 5), px(2, 6), px(1, 6)];
  }
  const tier = tool_tier(id);
  for (let i = 0; i < tier; i++) base.push([4 + i, 7]);
  return base;
}

// Block speckle (draw_world interior).  Furnace is dynamic (smelt/time),
// so it is handled separately in the mcb and excluded here.
const SPECKLE = {
  [B_GRASS]: [px(1, 1), px(4, 1), px(2, 4), px(5, 5)],
  [B_DIRT]: [px(2, 2), px(5, 3), px(1, 5), px(6, 6)],
  [B_STONE]: [px(2, 2), px(5, 4), px(3, 6)],
  [B_COBBLE]: [px(1, 1), px(4, 2), px(6, 1), px(2, 4), px(5, 5)],
  [B_BEDROCK]: [px(0, 0), px(3, 1), px(6, 0), px(1, 3), px(5, 3), px(2, 5), px(7, 4), px(4, 6)],
  [B_LOG]: v(2, 1, 6).concat(v(5, 1, 6)),
  [B_LEAVES]: [px(1, 1), px(4, 2), px(6, 1), px(2, 4), px(5, 5), px(3, 6)],
  [B_PLANKS]: [px(0, 2), px(2, 2), px(4, 2), px(6, 2), px(0, 5), px(2, 5), px(4, 5), px(6, 5)],
  [B_CRAFT]: rect(2, 2, 4, 4),
  [B_SAND]: [px(2, 2), px(6, 3), px(3, 5), px(5, 6)],
  [B_GRAVEL]: [px(1, 2), px(4, 1), px(6, 4), px(2, 5), px(5, 6)],
  [B_COAL]: [px(3, 3), px(4, 3), px(3, 4), px(4, 4), px(5, 2)],
  [B_IRON]: [px(2, 2), px(5, 3), px(3, 5), px(5, 5)],
  [B_DIAMOND]: [px(4, 2), px(3, 3), px(5, 3), px(4, 4)],
  [B_OBSIDIAN]: [px(1, 1), px(2, 2), px(3, 3), px(4, 4), px(5, 5), px(6, 6), px(6, 1), px(5, 2), px(2, 5), px(1, 6)],
  [B_NETHERRACK]: [px(1, 2), px(4, 1), px(6, 4), px(2, 5), px(5, 6)],
  [B_NBRICK]: [px(0, 3), px(2, 3), px(4, 3), px(6, 3)].concat(v(4, 0, 2), v(2, 4, 7)),
  [B_SBRICK]: [px(0, 3), px(2, 3), px(4, 3), px(6, 3)].concat(v(4, 0, 2), v(2, 4, 7)),
  [B_SPAWNER]: rect(1, 1, 6, 6).concat([px(2, 2)], [px(5, 2)], [px(3, 4)], [px(4, 4)], [px(2, 5)], [px(5, 5)]),
  [B_ENDSTONE]: [px(2, 1), px(5, 2), px(1, 4), px(4, 4), px(6, 6), px(3, 6)],
  [B_FRAME]: rect(1, 2, 6, 5).concat([px(3, 4)], [px(4, 4)]),
  [B_FRAME_EYE]: rect(1, 2, 6, 5).concat([px(3, 3)], [px(4, 3)], [px(3, 4)], [px(4, 4)], [px(2, 4)], [px(5, 4)]),
};

// Pixel list for any icon id (blocks, items, tools).  null if none.
function icon_pixels(id) {
  if (ICON[id]) return ICON[id];
  if (id >= I_WPICK && id <= I_DSWORD) return tool_sprite(id);
  return null;
}

// Pixel list for a block speckle id.  null if none (furnace is dynamic).
function speckle_pixels(id) {
  return SPECKLE[id] || null;
}

module.exports = {
  B_AIR, B_GRASS, B_DIRT, B_STONE, B_COBBLE, B_BEDROCK,
  B_LOG, B_LEAVES, B_PLANKS, B_CRAFT, B_FURNACE,
  B_SAND, B_GRAVEL, B_COAL, B_IRON, B_DIAMOND,
  B_WATER, B_LAVA, B_OBSIDIAN, B_PORTAL,
  B_NETHERRACK, B_NBRICK, B_SPAWNER, B_ENDSTONE,
  B_SBRICK, B_FRAME, B_FRAME_EYE, B_ENDPORTAL,
  I_STICK, I_COAL, I_FLINT, I_IRONING, I_DIAMOND,
  I_BUCKET, I_BUCKET_W, I_BUCKET_L, I_FSTEEL, I_ROD,
  I_POWDER, I_PEARL, I_EYE,
  I_WPICK, I_WAXE, I_WSWORD, I_SPICK, I_SAXE, I_SSWORD,
  I_IPICK, I_IAXE, I_ISWORD, I_DPICK, I_DAXE, I_DSWORD,
  SOLID, FONT, glyph_of, tool_sprite, icon_pixels, speckle_pixels, ICON, SPECKLE,
};
