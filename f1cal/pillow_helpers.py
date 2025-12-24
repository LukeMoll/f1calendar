"""
    Copied from fridgemagnet project
"""
import typing
from PIL import Image, ImageDraw, ImageFont
from bottle import request, response
from io import BytesIO
from typing import Generator

from .palettes import Inky as InkyCol, Palette


def break_lines(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont, width: int) -> Generator[
        str, None, None]:
    """
        Split `str` into multiple strings, such that they all fit within `width` when drawn with `font`.
    """
    words = text.split()

    while len(words) > 0:
        # Assume that all the words will fit on one line.
        line = words.copy()

        line_width = draw.textlength(' '.join(line), font=font)
        while line_width > width:
            line.pop()
            line_width = draw.textlength(' '.join(line), font=font)

        if len(line) == 0:
            # we couldn't "fit" any words on - so put one on anyway, so we don't get stuck.
            line.append(words.pop(0))

        # remove the words in `words` that are now also in `line`
        del words[:len(line)]
        yield ' '.join(line)


class EPaperDisplay:
    palette: type[Palette]
    WIDTH: int
    HEIGHT: int

    def __init__(self, p: type[Palette], w: int, h: int):
        self.palette = p
        self.WIDTH = w
        self.HEIGHT = h


EPD_INKY = EPaperDisplay(InkyCol, 800, 480)


def serve_image(route_handler: callable, epd: EPaperDisplay):
    def wrapper(*args, **kwargs):
        if request.query.format.lower() not in {'png', 'bmp'}:
            imgformat = 'png'
            print("Warning: ?format= not provided. Falling back to png.")
        else:
            imgformat = request.query.format.lower()

        imgformat: typing.Literal['png', 'bmp']

        # This depends on the enum having WHITE defined.
        # noinspection PyUnresolvedReferences
        img = Image.new("P", (epd.WIDTH, epd.HEIGHT), color=epd.palette.WHITE.value)
        img.putpalette(epd.palette.to_palette())
        draw = ImageDraw.Draw(img)

        route_handler(draw, *args, epd=epd, **kwargs)

        # https://stackoverflow.com/a/10170635
        img_io = BytesIO()
        if imgformat == 'png':
            img.save(img_io, format='PNG', optimize=True, bits=epd.palette.palette_bits())
        elif imgformat == 'bmp':
            img.save(img_io, format='BMP', optimize=True, bits=epd.palette.palette_bits())

        img_io.seek(0)

        content_type = f"image/{imgformat}"
        response.set_header('Content-type', content_type)
        return img_io.read()

    return wrapper


def serve_image_inky(r_h: callable):
    return serve_image(r_h, EPD_INKY)
