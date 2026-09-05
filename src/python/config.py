from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .pyriscv_definition import *


class TextStoragePosition(Enum):
    MINECRAFT_STORAGE = 0
    MINECRAFT_FUNCTION = 1


def generate_default_instruction_function_expand():
    res = {}
    for _, v in INSTRUCTION_LIST.items():
        for k in v:
            res[k] = False
    return res


class PyriscvConfig(BaseModel):
    text_storage_position: TextStoragePosition = TextStoragePosition.MINECRAFT_STORAGE

    # When true, the corresponding instruction will be inline expanded.
    # Only works when text_storage_position is MINECRAFT_FUNCTION
    instruction_function_expand: dict[str, bool] = Field(
        default_factory=generate_default_instruction_function_expand
    )

    # empty namespace for instructions
    # recommanded to be short for performance (I guess)
    instruction_namespace: str = "a"

    # empty namespace for instruction functions
    # recommanded to be short for performance (I guess)
    instruction_function_namespace: str = "b"

    # Whether to cache stage 2
    stage_2_cache: bool = True

    # ---- standardized screen, MC side only (ecall 2000-2003) --------
    # Keep in sync with pyriscv (app/gfx-saver) and plugin/screen_gen.py.
    #
    # screen_enabled=False builds the screen out entirely: screen_gen.py
    # emits only no-op ecall handlers, nothing is registered in the
    # minecraft:tick tag, and reload skips screen:init (see the
    # IF (config.screenEnabled) in org_jawbts_riscvmc2_main).  A guest
    # using ecall 2000-2003 then just gets no-ops.
    screen_enabled: bool = True

    # Screen size in pixels (content columns x rows, default 192 x 168,
    # matching the pyriscv demo).  A size change must be applied to every
    # place that sizes the screen:
    #   - this config (screen_width / screen_height);
    #   - pyriscv app/gfx-saver/main.c (SCR_W / SCR_H) -- rebuild the
    #     guest .mem and re-run this build;
    #   - pyriscv app/c-common/link.ld (SCREENFB LENGTH) -- only when the
    #     fb no longer fits (0x80000 covers up to 131072 pixels);
    #   - windowed pyriscv runs: --width/--height to match.
    # Position / orientation / enabled (screen_origin / screen_facing /
    # screen_top / screen_enabled below) are MC-side only -- the guest
    # never needs to know them.
    screen_width: int = Field(default=192, gt=0)
    screen_height: int = Field(default=168, gt=0)

    # World block of the screen's TOP-LEFT pixel (content gx=0, gy=0).
    # The defaults reproduce the classic wall at x 0..191, y 64..231,
    # z = 0: for vertical walls rows go down (pixel y = origin_y - gy).
    screen_origin: tuple[int, int, int] = (0, 231, 0)

    # Compass/axis direction the screen front (painted side) faces.
    # Vertical walls: north/south/east/west.  Horizontal screens (a floor
    # or a ceiling): "up" / "down", read with the content top pointing at
    # screen_top; that field is ignored for vertical walls.
    screen_facing: Literal[
        "north", "south", "east", "west", "up", "down"
    ] = "south"

    # For horizontal screens (screen_facing up/down): the compass
    # direction the content's top edge (row 0) points at.  "north" lays
    # the picture out like a map with its top toward -z.
    screen_top: Literal["north", "south", "east", "west"] = "north"

    def set_expand_instruction_function(
        self, instruction_functions_to_expand: list[str]
    ):
        for f in instruction_functions_to_expand:
            if f not in self.instruction_function_expand:
                raise ValueError(f"Unknown instruction function: {f}")
            self.instruction_function_expand[f] = True
