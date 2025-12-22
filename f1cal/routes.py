from .pillow_helpers import serve_image_inky, EPaperDisplay, InkyCol

from bottle import route, run, request, abort
from PIL import ImageDraw

@route('/')
def index():
    return "Hello, world!"

@route('/inky/hello')
@serve_image_inky
def hello_inky(draw : ImageDraw, epd : EPaperDisplay):
    """
        "Test pattern" colour bars
    """
    TOTAL_WIDTH = 800
    TOTAL_HEIGHT = 480
    NUM_COLS = len(InkyCol)
    print(f"{NUM_COLS=}")
    COL_WIDTH = TOTAL_WIDTH / NUM_COLS

    for i,colour in enumerate(InkyCol):
        start_xy = (i*COL_WIDTH, 0)
        end_xy = ((i+1)*COL_WIDTH, 480)
        print(i, colour, start_xy, end_xy)
        draw.rectangle([start_xy, end_xy], fill=colour.value, width=0)
