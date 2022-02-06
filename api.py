from fastapi import FastAPI, HTTPException


app = FastAPI()


@app.post("/shutdown")
async def read_item():
    return {"action": "successful"}


@app.get("/brightness/get")
async def get_brightness():
    return {"brightness": shared_values["brightness"]}


@app.post("/brightness/set")
async def set_brightness(new_brightness: int):
    if new_brightness > 100 or new_brightness < 0:
        return HTTPException(status_code=406, detail="Value out of Range")

    shared_values["brightness"] = new_brightness
    return {"action": "successful"}
