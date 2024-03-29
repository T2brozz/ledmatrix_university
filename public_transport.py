from datetime import datetime
from json import dumps, loads

import redis
import requests

r = redis.Redis()


def get_departures(station_name: int, directions: list[str] = [], departures_per_direction=1) -> dict[str, list]:
    """
    returns for specified direction the departures of an station form the VAG/VGN public transport network

    :param station_name: Vgn id of station/ get it with https://start.vag.de/dm/api/v1/haltestellen/VGN?name=stationname
    :param directions: List of direction to prioritize, leave empty for all directions
    :param departures_per_direction: how many departures for each direction
    :return:   dict with a list for each direction
    """

    rq = requests.get(f"https://start.vag.de/dm/api/v1/abfahrten/VAG/{station_name}?product=Tram&limitcount=2")
    if rq.status_code != 200:
        r.set("public_transport", dumps(
            {str("Error" + str(rq.status_code)): [{
                "line": "0",
                "typ": "None",
                "time": "0:00:00",
                "delay": "0:00:00",
            }]}
        ))

    result = rq.json()["Abfahrten"]
    result = sorted(result, key=lambda x: x["AbfahrtszeitSoll"])
    departures = {}
    for departure in result:
        if (direction := departure["Richtungstext"]) in directions or len(directions) == 0:
            if direction is not departure.keys():
                departures[direction] = []
            if len(departures[direction]) < departures_per_direction:
                departures[direction].append(
                    {
                        "line": departure["Linienname"],
                        "typ": departure["Produkt"],
                        "time": str(
                            (time := datetime.strptime(departure["AbfahrtszeitSoll"], "%Y-%m-%dT%H:%M:%S%z"))),
                        "delay": str(datetime.strptime(departure["AbfahrtszeitIst"], "%Y-%m-%dT%H:%M:%S%z") - time),
                    }
                )

    r.set("public_transport", dumps(departures))
    return departures


def start():
    get_departures("DEICHS")  # ['Erlenstegen', 'Doku-Zentrum']
    print(loads(r.get("public_transport")))


if __name__ == '__main__':
    start()
    ##print(get_departures(335))  # ['Erlenstegen', 'Doku-Zentrum']
    ##print(loads(r.get("public_transport")))
