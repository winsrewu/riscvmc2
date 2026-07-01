from enum import Enum
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

    # Whether to cache stage 2
    stage_2_cache: bool = True