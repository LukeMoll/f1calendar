"""
    Copied from fridgemagnet project
"""

import math
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum, EnumMeta, auto


class _AbstractEnumMeta(EnumMeta, ABCMeta):
    pass


class Palette(ABC, Enum, metaclass=_AbstractEnumMeta):

    @abstractmethod
    def to_rgb(self) -> tuple[int, int, int]:
        raise NotImplemented

    @classmethod
    def to_palette(cls) -> list[int]:
        # Compatible with
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.putpalette
        # Potentially don't need to extend it to 256 colours?
        palette = [0, 0, 0] * 256

        for i, e in enumerate(cls):
            # Iterate over enum values
            palette[(i * 3):(i * 3) + 3] = e.to_rgb()

        return palette

    @classmethod
    def palette_bits(cls) -> int:
        return math.ceil(math.log2(len(cls)))


class Inky(Palette):
    BLACK = 0
    WHITE = auto()
    GREEN = auto()
    BLUE = auto()
    RED = auto()
    YELLOW = auto()
    ORANGE = auto()
    TAUPE = auto()

    # noinspection PyRedundantParentheses
    def to_rgb(self) -> tuple[int, int, int]:
        # https://github.com/pimoroni/inky/issues/115#issuecomment-872426157
        match self:
            case Inky.BLACK:
                return (0, 0, 0)
            case Inky.WHITE:
                return (255, 255, 255)
            case Inky.GREEN:
                return (0, 255, 0)
            case Inky.BLUE:
                return (0, 0, 255)
            case Inky.RED:
                return (255, 0, 0)
            case Inky.YELLOW:
                return (255, 255, 0)
            case Inky.ORANGE:
                return (255, 140, 0)
            case Inky.TAUPE:
                return (255, 255, 255)
            case _:
                raise IndexError(f"Invalid colour {self.value} for {self.__class__.__name__}")


def main():
    for pal in (Inky,):
        print(f"--- {pal.__name__}: {len(pal)} values ({pal.palette_bits()} bits) ---")
        for i, e in enumerate(pal):
            print(i, e.name, e.value, e.to_rgb())
        print("---")
        lst = pal.to_palette()
        for i in range(len(lst) // 3):
            section = lst[i * 3:(i * 3) + 3]
            if section != [0, 0, 0]:
                print(i, section)


if __name__ == "__main__":
    main()  # Use main function so this code doesn't trigger `Shadows name from outer scope` warnings.
