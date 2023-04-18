import threading
import time

import uvicorn

import api
import mensa
import public_transport
import redis

r = redis.Redis()


def api_start():
    uvicorn.run('api:app', host='0.0.0.0', port=8080, debug=False)


def crawl_data():
    time.sleep(10)
    c = 0
    try:
        public_transport.start()
    except:
        r.set("public_transport", '{"Error": [{"line": "0", "typ": "None", "time": "0:00:00", "delay": "0:00:00"}]}')

    try:
        mensa.start()
    except Exception as e:
        r.set("canteen", '[{"canteen": "Error", "name": "Fuckin Error", "price": 1}]')

    while True:
        c += 1
        if c % 5 == 0:
            try:
                public_transport.start()
            except:
                r.set("public_transport",
                      '{"Error": [{"line": "0", "typ": "None", "time": "0:00:00", "delay": "0:00:00"}]}')
        if c >= 60:
            try:
                mensa.start()
            except Exception as e:
                r.set("canteen", '[{"canteen": "Error", "name": "Fuckin Error", "price": 1}]')

            c = 0
        time.sleep(60)


def start_everything():
    thread1 = threading.Thread(target=api_start, name="api")
    thread2 = threading.Thread(target=crawl_data, name="data crawler")
    thread1.start()
    thread2.start()
