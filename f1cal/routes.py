from .pillow_helpers import serve_image_inky, EPaperDisplay, InkyCol, break_lines
from .font import F1Reg, F1Bold, F1Wide
from .data_sources import schedule

from bottle import route, run, request, abort
from PIL import ImageDraw
from datetime import datetime as dt, timezone as tz


@route('/')
def index():
    return "Hello, world!"

@route('/inky/hello')
@serve_image_inky
def hello_inky(draw : ImageDraw, epd : EPaperDisplay):
    """
        "Test pattern" colour bars
    """
    NUM_COLS = len(InkyCol)
    print(f"{NUM_COLS=}")
    COL_WIDTH = epd.WIDTH / NUM_COLS

    for i,colour in enumerate(InkyCol):
        start_xy = (i*COL_WIDTH, 0)
        end_xy = ((i+1)*COL_WIDTH, epd.HEIGHT)
        print(i, colour, start_xy, end_xy)
        draw.rectangle([start_xy, end_xy], fill=colour.value, width=0)

@route('/inky/text')
@serve_image_inky
def text_inky(draw : ImageDraw, epd : EPaperDisplay):
    draw.rectangle([0,0,epd.WIDTH,epd.HEIGHT], fill=InkyCol.RED.value)

    draw.text([5, 5], text="2022 British Grand Prix", font=F1Wide(21), fill=InkyCol.BLACK.value)

    margin = epd.WIDTH * 0.05

    active_width = epd.WIDTH - margin * 2

    script1 = "\"Leclerc has that inside line. Perez goes off the track, cuts the chicane. Off goes Leclerc...\""
    script2 = "Through goes Hamilton, unbelievable stuff!"

    script1_y = margin

    font = F1Reg(36)
    lines = list(break_lines(script1, draw, font, active_width))
    draw.multiline_text([epd.WIDTH/2, script1_y], anchor="ma", text='\n'.join(lines), fill=InkyCol.BLACK.value, font=font)
    bbox1 = draw.multiline_textbbox([epd.WIDTH/2, script1_y], anchor="ma", text='\n'.join(lines), font=font)

    script2 = script2.upper()
    font=F1Bold(56)
    lines = list(break_lines(script2, draw, font, active_width))
    draw.multiline_text([
        bbox1[0],
        bbox1[3] + margin/2
        ],
        anchor="la",
        text='\n'.join(lines), fill=InkyCol.WHITE.value, font=font)

    script3 = "123456790"
    pt = epd.WIDTH / len(script3)

    while True:
        lines = list(break_lines(script3, draw, F1Bold(pt), epd.WIDTH))
        if len(lines) > 1:
            pt -= 2
        else:
            break
    draw.multiline_text([epd.WIDTH, epd.HEIGHT], anchor="rd", text=script3, fill=InkyCol.ORANGE.value, font=F1Bold(pt))

@route('/inky/countdown')
@serve_image_inky
def countdown_inky(draw : ImageDraw, epd : EPaperDisplay):
    next_gp = schedule.get_next_grand_prix()
    days : int = (next_gp.DTSTART - dt.now(tz.utc)).days
    
    draw.rectangle([0,0, epd.WIDTH, epd.WIDTH], fill=InkyCol.BLACK.value)

    font = F1Bold(300)

    # Draw number in center of screen
    draw.text(
        [
            epd.WIDTH/2,
            epd.HEIGHT/2
        ],
        anchor="mm",
        text=str(days),
        font=font,
        fill=InkyCol.WHITE.value
    )

    bb = draw.textbbox(
        [
            epd.WIDTH/2,
            epd.HEIGHT/2
        ],
        anchor="mm",
        text=str(days), font=font)

    caption = "days to go"
    draw.text(
        [
            epd.WIDTH/2,
            bb[3] + 8
        ],
        anchor="ma",
        text=caption,
        font=F1Reg(52),
        fill=InkyCol.RED.value
    )
    
    draw.text([0,0], anchor="la", text="2026 Formula 1 World Champtionship", font=F1Wide(18), fill=InkyCol.WHITE.value)
