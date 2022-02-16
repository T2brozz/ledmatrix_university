import datetime
from json import dumps, loads

import redis
import uvicorn as uvicorn
from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

r = redis.Redis()
app = FastAPI()

app.mount("/static", StaticFiles(directory="templates"), name="static")

templates = Jinja2Templates(directory="templates")


class TimerAutoOnOff(BaseModel):
    Monday: datetime.time
    Tuesday: datetime.time
    Wednesday: datetime.time
    Thursday: datetime.time
    Friday: datetime.time
    Saturday: datetime.time
    Sunday: datetime.time


def myconverter(o):
    if isinstance(o, datetime.time):
        return o.__str__()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": 40})


@app.post("/shutdown")
async def read_item():
    return {"action": "successful"}


@app.get("/brightness/get")
async def get_brightness():
    return {"brightness": r.get("brightness")}


@app.post("/brightness/set")
async def set_brightness(new_brightness: int):
    if new_brightness > 100 or new_brightness < 0:
        return HTTPException(status_code=406, detail="Value out of Range")
    r.set("brightness", new_brightness)
    return {"action": "successful"}


@app.post("/text")
async def set_text(line1="", line2="", line3=""):
    r.set("lines", dumps([line1, line2, line3]))
    return {"action": "successful"}


@app.get("/text")
async def get_text():
    lines = loads(r.get("lines"))
    return {'line1': lines[0], 'line2': lines[2], 'line3': lines[2]}


@app.post("/autodisplay/")
async def set_display_auto_onoff(on: TimerAutoOnOff, off: TimerAutoOnOff):
    r.set("on", dumps(on.dict(), default=myconverter))
    r.set("off", dumps(off.dict(), default=myconverter))
    print(r.get("on"))
    print(r.get("off"))
    return {"action": "successful"}


@app.get("/autodisplay/")
async def get_display_auto_onoff():
    return {'on': loads(r.get("on")), 'off': loads(r.get("off"))}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, debug=True)
