#!/usr/bin/python3
import datetime
import sys
from datetime import datetime, time
from json import loads
from time import sleep

import redis
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

canvas = None
font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/10x20.bdf")

textColor = graphics.Color(255, 255, 255)
r = redis.Redis()
scroll_speed = 1
refreshrate = 60
next_module = {"mensa": False, "custom": False, "custom_timer": 20 * refreshrate, "vgn": 20 * refreshrate}


def render_vgn():
    json = loads(r.get("public_transport"))
    for i, (key, value) in enumerate(json.items()):
        graphics.DrawText(canvas, font, 2, font.height * (i + 1), graphics.Color(30, 129, 176), value[0]["line"])
        graphics.DrawText(canvas, font, 15, font.height * (i + 1), textColor, key)
        graphics.DrawText(canvas, font, 167, font.height * (i + 1), graphics.Color(153, 204, 255),
                          value[0]["time"][11:16])
        if (delay := value[0]['delay']) != '0:00:00':
            graphics.DrawText(canvas, font, 220, font.height * (i + 1), graphics.Color(255, 51, 0), f'+{delay[2:4]}')


def render_mensa(name_offset):
    json = loads(r.get("canteen"))

    longest_name = len(max(json, key=lambda x: len(x['name']))["name"]) * 10
    if name_offset == -longest_name - 65:
        name_offset = 1
        next_module["mensa"] = True
    for i, meal in enumerate(json):
        graphics.DrawText(canvas, font, name_offset, font.height * (i + 1), graphics.Color(30, 129, 176),
                          (meal['name'] + "  *|*  ") * 10)
        graphics.DrawText(canvas, font, 190, font.height * (i + 1), graphics.Color(0, 0, 0), "███████")
        graphics.DrawText(canvas, font, 200, font.height * (i + 1), textColor, str(meal['price']) + '€')
    name_offset -= scroll_speed
    return name_offset


def custom_text(name_offsets):
    lines = loads(r.get("lines"))
    for i, line in enumerate(lines):
        if name_offsets[i] == -len(line) * 10:
            name_offsets[i] = 1
            next_module['custom'] = True
        if line == "":
            name_offsets[i] = 1
            next_module['custom'] = True
            return

    for i, line in enumerate(lines):
        graphics.DrawText(canvas, font, name_offsets[i], font.height * (i + 1), textColor, line)

    if not any([True if len(x) > 256 else False for x in lines]):
        next_module['custom_timer'] -= 1
        return name_offsets
    for i, line in enumerate(lines):
        if len(line) * 10 > 256:
            name_offsets[i] -= scroll_speed

    return name_offsets


def autoonoff():
    dayname = datetime.strftime(datetime.now(), "%A")
    on = time.fromisoformat(loads(r.get("on")).get(dayname))
    off = time.fromisoformat(loads(r.get("off")).get(dayname))
    if off <= on:
        return False
    if on <= datetime.now().time() <= off:
        return True
    return False
    # on ={day:datetime.time.fromisoformat(ontime) for day,ontime in  loads(r.get("on")).items()}
    # off ={day:datetime.time.fromisoformat(offtime) for day,offtime in  loads(r.get("offtime")).items()}


def start_matrix():
    global canvas
    global next_module
    # Configuration for the matrix
    canvas = matrix.CreateFrameCanvas()
    canvas.Clear()
    try:
        print("Press CTRL-C to stop.")
        mensa_name_offset = 0
        customline_offset = [0, 0, 0]
        while True:
            canvas.Clear()
            if autoonoff():
                # module contolling
                if not next_module["mensa"]:
                    mensa_name_offset = render_mensa(mensa_name_offset)
                elif not next_module['custom'] and next_module['custom_timer'] >= 0:
                    customline_offset = custom_text(customline_offset)
                elif next_module['vgn'] >= 0:
                    next_module["vgn"] -= 1
                    render_vgn()
                else:
                    next_module = {"mensa": False, "custom": False, "custom_timer": 20 * refreshrate,
                                   "vgn": 20 * refreshrate}

                # controls brightness
                brightness = 50  # int(r.get('brightness'))
                if brightness > 0:
                    matrix.brightness = brightness
                    canvas = matrix.SwapOnVSync(canvas)
                    sleep(1 / refreshrate)

                else:
                    matrix.Fill(0, 0, 0)
                    sleep(1)

            else:
                sleep(60)

    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.brightness = 100
    options.chain_length = 4
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
    options.led_rgb_sequence = "RGB"
    options.drop_privileges = False
    options.disable_hardware_pulsing = True
    # options.show_refresh_rate=True
    # options.limit_refresh_rate_hz = 70
    matrix = RGBMatrix(options=options)
    r.set('brightness', 100)
    # print(autoonoff())
    start_matrix()
