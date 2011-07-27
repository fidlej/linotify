
import time
import random
import logging
from google.appengine.ext import db

from src.model import Server, Point
from src import store

PRESEVED_DAYS = 32

def remove_old_points():
    server_keys = Server.all(keys_only=True)
    key = random.choice(list(server_keys))
    server_id = key.id()

    outdated_timestamp = time.time() - 24*3600*PRESEVED_DAYS
    shortest_duration = store.STAGE_DURATIONS[0]
    outdated_id = Point.build_key_name(server_id, shortest_duration,
            outdated_timestamp)
    outdated_key = db.Key.from_path("Point", outdated_id)
    query = db.GqlQuery(
            "select __key__ from Point where __key__ <= :outdated_key",
            outdated_key=outdated_key)
    point_keys = query.fetch(limit=1000)
    info = "outdated points at server %s: %s (e.g., %s)" % (
            server_id, len(point_keys), point_keys[:1])
    logging.info(info)
    db.delete(point_keys)
    return info

