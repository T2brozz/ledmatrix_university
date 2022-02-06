#!/usr/bin/python3
import sys
import time
from json import loads
import redis
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

canvas = None
font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/10x20.bdf")

textColor = graphics.Color(255, 255, 255)
r = redis.Redis()
scroll_speed=1

def render_vgn():
    json = loads(r.get("public_transport"))
    for i, (key, value) in enumerate(json.items()):
        graphics.DrawText(canvas,font,2,font.height * (i+1),graphics.Color(30,129,176),value[0]["line"])
        graphics.DrawText(canvas, font, 15, font.height * (i+1), textColor, key)
        graphics.DrawText(canvas,font,167,font.height * (i+1),graphics.Color(153, 204, 255),value[0]["time"][11:16])
        if (delay:=value[0]['delay'])!='0:00:00':
            graphics.DrawText(canvas,font,220,font.height * (i+1),graphics.Color(255, 51, 0),f'+{delay[2:4]}')

def render_mensa(name_offset):
    json = loads(r.get("canteen"))

    longest_name=len(max(json, key=lambda x:len(x['name']))["name"])*10
    if name_offset==-longest_name-65:
        name_offset=0
    for i, meal in enumerate(json):
        graphics.DrawText(canvas, font, name_offset, font.height * (i + 1), graphics.Color(30, 129, 176), (meal['name']+"  *|*  ")*10)
        graphics.DrawText(canvas,font,190,font.height * (i + 1),graphics.Color(0,0,0),"███████")
        graphics.DrawText(canvas, font, 200, font.height * (i + 1), textColor, str(meal['price'])+'€')
    name_offset-=scroll_speed
    return name_offset

def start_matrix():
    global canvas
    # Configuration for the matrix

    canvas = matrix.CreateFrameCanvas()
    canvas.Clear()
    try:
        print("Press CTRL-C to stop.")
        name_offset=0
        while True:
            canvas.Clear()
            name_offset=render_mensa(name_offset)
            #render_vgn()
            canvas = matrix.SwapOnVSync(canvas)

            time.sleep(1 / 60)

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
    # options.limit_refresh_rate_hz = 70
    matrix = RGBMatrix(options=options)

    start_matrix()
