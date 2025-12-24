import time
import gc

import machine

import ntptime

from urllib import urequest
import inky_helper as ih
from inky_frame import BLACK, WHITE, GREEN, BLUE, RED, YELLOW, ORANGE, TAUPE
import inky_frame
PALETTE = [BLACK, WHITE, GREEN, BLUE, RED, YELLOW, ORANGE, TAUPE]
from picographics import DISPLAY_INKY_FRAME_7 as DISPLAY, PicoGraphics
import pngdec

WIFI_NUM_ATTEMPTS = 1
NTP_NUM_ATTEMPTS = 5
NTP_TIMEOUT_SECONDS = 15

ERROR_BOX_TITLE_WEIGHT = 2
ERROR_BOX_MESSAGE_WEIGHT = 1
ERROR_BOX_FONT_SCALE = 2
ERROR_BOX_MAX_WIDTH_PROPORTION = 0.5
ERROR_BOX_NUM_LINES = 5

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
    except ImportError:
        print("Create secrets.py with WIFI_SSID and WIFI_PASSWORD")
        return False
    except Exception as e:
        print("Other exception:", e)
        return False

def disconnect_wifi():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    ih.stop_network_led()


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
        return True
    except OSError as e:
        print("Unable to contact NTP server:", e)
        return False

def draw_image_from_web():
    """
        Download an indexed PNG and draw it on the screen
    """
    from secrets import ENDPOINT
    # bars.png is an indexed 480x800 image.
    url = ENDPOINT + "countdown?format=png"
    print("Opening", url)
    
    data = download_to_ram(url)
    if data is None:
        print("Download failed!")
        return False
    print(f"Download succeeded with buffer size {len(data)}")
    
    try:
        png = pngdec.PNG(graphics)
        png.open_RAM(data)
        png.decode()
        return True
    except RuntimeError as e:
        print("PNG error:", e)
        return False
    
def draw_time(bg=WHITE, fg=BLACK):
    graphics.set_font("bitmap8")
    
    rtc = machine.RTC()
    current_t = rtc.datetime()
    date_str = f"{current_t[2]}/{current_t[1]}/{current_t[0]}"
    time_str = f"{current_t[4]}:{current_t[5]:02}:{current_t[6]:02}"
    
    # Measure again with final scale
    width_date = graphics.measure_text(date_str)
    width_time = graphics.measure_text(time_str)
    text_width = max(width_date,width_time)
    
    line_height = 16
    margin = 4
    
    graphics.set_pen(bg)
    # TODO: update after buttons are implemented
    y0 = int(HEIGHT - ((line_height + margin) * 2))
    graphics.rectangle (
        0,
        y0,
        int(text_width + margin * 2),
        HEIGHT
    )
    
    graphics.set_pen(fg)
    graphics.text(time_str, int(margin), y0 + margin)
    graphics.text(date_str, int(margin), y0 + margin + line_height)
    
    
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
    except MemoryError:
        print("MemoryError!")
        return # None
    finally:
        socket.close()
        gc.collect()

def draw_error_box(error_title, error_text):
    graphics.set_pen(TAUPE)
    graphics.clear()
    
    graphics.set_font("bitmap8")

    box_width = int(WIDTH * ERROR_BOX_MAX_WIDTH_PROPORTION)
    if (measured_width := graphics.measure_text(error_text, ERROR_BOX_FONT_SCALE)) < box_width:
        box_width = measured_width
    # Otherwise, the text will wrap.    
    
    # Picographics (Python bindings, at least) doesn't provide a way to measure the height of wrapped text
    # Nor if it has wrapped, or the number of times it has wrapped.
    # Instead we'll just assume that there's so many lines of text and accomodate for that.
    line_height = int(ERROR_BOX_FONT_SCALE * 9)
    box_height = int(ERROR_BOX_NUM_LINES * line_height)
    
    x0 = int((WIDTH - box_width) / 2)
    y0 = int((HEIGHT - box_height) / 2)
    margin = 5
    
    
    # Draw background box (plus margin)
    graphics.set_pen(WHITE)
    graphics.rectangle(x0, y0, box_width, box_height)
    graphics.set_pen(BLACK)
    graphics.line(x0, y0, x0 + box_width, y0)
    graphics.line(x0 + box_width, y0, x0 + box_width, y0 + box_height)
    graphics.line(x0, y0 + box_height, x0 + box_width, y0 + box_height)
    graphics.line(x0, y0, x0, y0 + box_height)
    
    # `scale` argument for bitmap fonts doesn't work.
    title_width = graphics.measure_text(error_title) * ERROR_BOX_FONT_SCALE
    graphics.set_pen(RED)
    graphics.text(error_title, int(x0 + title_width/2), y0 + margin, scale=ERROR_BOX_FONT_SCALE)
    
    graphics.set_pen(BLACK)
    # Wordwrap doesn't look like it works with vector fonts - need to implement our own method >.<
    graphics.text(error_text, x0 + margin, y0 + margin +line_height , wordwrap=box_width-(margin * 2), scale=ERROR_BOX_FONT_SCALE)


def update_epd():    
    ih.led_warn.on()
    graphics.update()
    ih.led_warn.off()

def initialise():
    global graphics, WIDTH, HEIGHT
    # To allow USB to initialise
    time.sleep(1)

    ih.clear_button_leds()
    ih.led_warn.off()

    graphics = PicoGraphics(DISPLAY)
    WIDTH, HEIGHT = graphics.get_bounds()
    print(f"Initialised display (type={DISPLAY}), {WIDTH}x{HEIGHT}")

if __name__ == "__main__":
    try:
        initialise()
    except Exception as e:
        print("Error occurred while initialising:")
        print(e)
        
    # Connect to WiFi
    for i in range(WIFI_NUM_ATTEMPTS):
        if (wifi_connected := connect_wifi()):
            break
    if not wifi_connected:
        print(f"Failed to connect to WiFi after {WIFI_NUM_ATTEMPTS} attempts.")
        draw_error_box("Network error", "Could not connect to WiFI. Check that the network SSID and password are correct.")
        update_epd()
        print("update_epd done")
        inky_frame.turn_off()
        
        
    # (this could go _after_ image draw)
    for j in range(NTP_NUM_ATTEMPTS):
        if (ntp_success := update_rtc()):
            break
    if not ntp_success:
        print(f"Failed to update RTC.")
    
    if not draw_image_from_web():
        draw_error_box("HTTP error", "Could not connect to the remote server.")
    else:
        ...
        # TODO: draw buttons
    
    disconnect_wifi()
    
    draw_time(BLACK, WHITE)
    
    update_epd()
    
    inky_frame.sleep_for(120) # minutes
    
        
