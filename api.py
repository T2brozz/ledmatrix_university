from fastapi import FastAPI, HTTPException
import redis
import datetime
r=redis.Redis()
app = FastAPI()


@app.post("/shutdown")
async def read_item():
    return {"action": "successful"}


@app.get("/brightness/get")
async def get_brightness():
    return {"brightness": await r.get("brightness")}


@app.post("/brightness/set")
async def set_brightness(new_brightness: int):
    if new_brightness > 100 or new_brightness < 0:
        return HTTPException(status_code=406, detail="Value out of Range")
    print(new_brightness)
    await r.set("brightness",new_brightness)
    return {"action": "successful"}

@app.post("/text/set")
async def set_text(line1="",line2="",line3=""):
    await r.set("line1",line1)
    await r.set("line2",line2)
    await r.set("line3",line3)
    return {"action": "successful"}

@app.post("/autodisplay/")
async  def set_display_auto_onoff(on:datetime.time):
        pass