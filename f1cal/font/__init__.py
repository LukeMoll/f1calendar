import os.path

from PIL import ImageFont
from typing import Callable


def load_otf(filename: str) -> Callable[[any], ImageFont.FreeTypeFont]:
    path = os.path.join(os.path.dirname(__file__), filename)

    def inner(*args, **kwargs):
        return ImageFont.truetype(path, *args, **kwargs)

    return inner


F1Reg = load_otf("Formula1-Regular.otf")
F1Bold = load_otf("Formula1-Bold.otf")
F1Wide = load_otf("Formula1-Wide.otf")
