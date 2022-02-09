import datetime
from json import dumps, loads

import redis
import requests

r = redis.Redis()


def get_mensa(mensa_id: int, day=datetime.date.today().strftime("%G-%m-%d"), mensa_name="") -> list[dict]:
    rq = requests.get(f"https://openmensa.org/api/v2/canteens/{mensa_id}/days/{day}/meals")
    if rq.status_code == 404:
        r.set("canteen", dumps([{
            'canteen': "",
            'name': "",
            'price': rq.status_code
        }]))
        return
    if rq.status_code != 200:
        r.set("canteen", dumps([{
            'canteen': mensa_name,
            'name': "Fuckin Error",
            'price': rq.status_code
        }]))
        raise ConnectionError
    result = rq.json()
    meals = []
    for meal in result:
        meals.append(
                {
                    'canteen': mensa_name,
                    'name': meal['name'],
                    'price': meal['prices']['students']
                }
        )
    r.set("canteen", dumps(meals))


if __name__ == '__main__':
    get_mensa(268, "2022-02-04", mensa_name='KA')
    # 269 HQ
    # 268 KA
    print(loads(r.get("canteen")))
