import datetime
from json import dumps, loads

import redis
import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

r = redis.Redis()
app = FastAPI()


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


@app.post("/text/set")
async def set_text(line1="", line2="", line3=""):
    r.set("lines", dumps([line1, line2, line3]))
    return {"action": "successful"}


@app.post("/autodisplay/")
async def set_display_auto_onoff(on: TimerAutoOnOff, off: TimerAutoOnOff):
    r.set("on", dumps(on.dict(), default=myconverter))
    r.set("off", dumps(off.dict(), default=myconverter))
    print(r.get("on"))
    print(r.get("off"))


@app.get("/autodisplay/")
async def get_display_auto_onoff():
    return {'on': loads(r.get("on")), 'off': loads(r.get("off"))}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80, debug=True)
