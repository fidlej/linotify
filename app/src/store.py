
from google.appengine.ext import db

from src.model import UserProfile, Server, Stage, Point

class NotFoundError(Exception):
    pass

LIMIT = 1000
STAGE_DURATIONS = [300, 3600]

def add_server(user_id, name):
    secret = _generate_server_secret()
    server = Server(user_id=user_id, name=name, secret=secret)
    server.put()
    server_id = server.id()

    stages = []
    for duration in STAGE_DURATIONS:
        stage = Stage.prepare(server_id, duration)
        stages.append(stage)

    db.put(stages)
    return server

def ensure_user_profile(user):
    profile = UserProfile.get_or_insert(user.user_id(), user=user)
    return profile

def _generate_server_secret(length=20):
    """Generates a random secret string.
    """
    # Thanks for the recipe:
    # http://code.activestate.com/recipes/59873/
    from random import choice
    import string
    chars = string.letters
    return ''.join(choice(chars) for i in xrange(length))

def find_servers(user_id, limit=LIMIT):
    query = Server.gql('where user_id = :user_id '
            'order by name, __key__',
            user_id=user_id)
    return query.fetch(limit)

def get_stage(server_id, duration):
    key_name = Stage.build_key_name(server_id, duration)
    stage = Stage.get_by_key_name(key_name)
    if stage is None:
        raise NotFoundError('No such stage: %s' % key_name)

    return stage

def get_first_stage(server_id):
    return get_stage(server_id, STAGE_DURATIONS[0])

def get_last_data_at(server_id):
    """Returns the timestamp of the last seend data
    or None.
    """
    stage = get_first_stage(server_id)
    return stage.last_data_at

def get_points(server_id, duration, time_from, time_to, limit=LIMIT):
    key_from = Point.build_key_name(server_id, duration, time_from)
    key_to = Point.build_key_name(server_id, duration, time_to)

    query = Point.gql("where __key__ > :key_from "
            "and __key__ <= :key_to "
            "order by __key__ ",
            key_from=db.Key.from_path('Point', key_from),
            key_to=db.Key.from_path('Point', key_to))
    return query.fetch(limit)

