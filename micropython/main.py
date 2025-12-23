import time
import gc

from urllib import urequest
import inky_helper as ih
from inky_frame import BLACK, WHITE, GREEN, BLUE, RED, YELLOW, ORANGE, TAUPE
PALETTE = [BLACK, WHITE, GREEN, BLUE, RED, YELLOW, ORANGE, TAUPE]
from picographics import DISPLAY_INKY_FRAME_7 as DISPLAY, PicoGraphics
import pngdec

# To allow USB to initialise
time.sleep(0.5)

ih.clear_button_leds()
ih.led_warn.off()

graphics = PicoGraphics(DISPLAY)
WIDTH, HEIGHT = graphics.get_bounds()
print(f"Initialised display (type={DISPLAY}), {WIDTH}x{HEIGHT}")
graphics.set_font("bitmap8")

def bars():
    graphics.set_pen(WHITE)
    graphics.clear()
    
    BAR_HEIGHT = int(HEIGHT // len(PALETTE))
    
    for i,color in enumerate(PALETTE):
        graphics.set_pen(color)
        
        graphics.rectangle(0, BAR_HEIGHT * i, WIDTH, BAR_HEIGHT * (i + 1))
        
    ih.led_warn.on()
    graphics.update()
    ih.led_warn.off()

def connect_wifi():
    try:
        from secrets import WIFI_PASSWORD, WIFI_SSID
        ih.network_connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected to network '{WIFI_SSID}'")
        return True
    except ImportError as e:
        print("Create secrets.py with WIFI_SSID and WIFI_PASSWORD", e)
        return False
    except e:
        print("Other exception:", e)
        return False

def get_img():
    from secrets import ENDPOINT
    # bars.png is an indexed 480x800 image.
    url = ENDPOINT + "bars.png"
    print("Opening", url)
    socket = urequest.urlopen(url)
    
    alloc = gc.mem_alloc()
    free = gc.mem_free()
    percent = alloc/(alloc+free)
    print(f"{alloc=}\n{free=}\n{percent=:.2%}")
    
    try:
        data = bytearray(4096)
        while True:
            # TODO: we need to get this all in one go.
            count = socket.readinto(data)
            if count == 0:
                break
            else: print(f"{count=}")
        print(f"Done reading")
        socket.close()
        gc.collect()
    except MemoryError as e:
        print(e)
        return
    
    png = pngdec.PNG(graphics)
    png.open_RAM(data)
    png.decode()
    
    ih.led_warn.on()
    graphics.update()
    ih.led_warn.off()
    

connect_wifi()
get_img()
# bars()
print("Done!")