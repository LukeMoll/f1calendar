import time
import gc

import machine
import ntptime

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
    """
        Draw horizontal bars on the screen with each colour
    """
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
    """
        Connect to WiFi (defined in secrets.py)
    """
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

def update_rtc():
    ntptime.timeout = 15
    
    rtc = machine.RTC()
    before_ticks_u = time.ticks_us()
    before_time_n = time.time_ns()
    try:
        ntptime.settime()
        after_ticks_u = time.ticks_us()
        after_time_n = time.time_ns()
        
        delta_time = (after_time_n - before_time_n) / 1_000_000_000
        delta_ticks = (after_ticks_u - before_ticks_u) / 1_000_000
        print(f"Updated time from NTP. Time difference = {delta_time:.1f} (elapsed {delta_ticks:.1f})")
        
        current_t = rtc.datetime()
        print(f"{current_t[0]}-{current_t[1]}-{current_t[2]} {current_t[4]}:{current_t[5]:02}:{current_t[6]:02}")
    except OSError as e:
        print("Unable to contact NTP server:", e)    

def draw_image_from_web():
    """
        Download an indexed PNG and draw it on the screen
    """
    from secrets import ENDPOINT
    # bars.png is an indexed 480x800 image.
    url = ENDPOINT + "bars.png"
    print("Opening", url)
    
    data = download_to_ram(url)
    print(f"Download succeeded with buffer size {len(data)}")
    
    png = pngdec.PNG(graphics)
    png.open_RAM(data)
    png.decode()
    
    ih.led_warn.on()
    graphics.update()
    ih.led_warn.off()
    
    
def download_to_ram(url):
    """
        Make a web request and store its output in a single bytearray. If the array is too small, the request is retried until we run out of RAM!
    """
    try:
        size = 128
        while True:
            socket = urequest.urlopen(url)
            data = bytearray(size)
            socket.readinto(data) # Read as much as we can into the buffer
            if socket.readinto(data) != 0:
                # There's still data left - so the buffer must not be big enough!
                print(f"Download failed with buffer size {size}")
                size *= 2
                data = None
                socket.close()
                gc.collect()
                continue
            else:
                # Full read was successful
                return data
    except MemoryError as e:
        print(e)
        return # None
    finally:
        socket.close()
        gc.collect()

if __name__ == "__main__":
    connect_wifi()
    update_rtc()
    # draw_image_from_web()
    # bars()
    print("Done!")
