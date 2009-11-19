
import time
import logging

from src import store
from src.model import Point, Server

LATEST_AGENT_VERSION = 'c73a6ab65e0f'

class _Measure(object):
    def __init__(self, sums, counts):
        self.sums = sums
        self.counts = counts

def parse_payload(payload):
    from django.utils import simplejson
    return simplejson.loads(payload)

def comment_agent_version(data):
    version = data.get('version')
    if version != LATEST_AGENT_VERSION:
        return 'newer agent available: %s' % LATEST_AGENT_VERSION
    return 'OK'

def update_stats(data):
    agentKey = data['serverKey']
    server_id = _check_server_secret(agentKey)

    current_time = int(time.time())
    stats = data['stats']
    logging.debug('collected stats: %s', stats)

    _update_stages(server_id, stats, current_time)

def _update_stages(server_id, stats, current_time):
    counts = dict(stats)
    for key in counts.iterkeys():
        counts[key] = 1

    measure = _Measure(stats, counts)
    _fill_stage(server_id, 0, measure, current_time)

def _fill_stage(server_id, stage_index, measure, current_time):
    """Updates a staging area with sampled values.
    A finished staging area produces a data point.
    The data point could feed a higher stage.
    """
    stage = store.get_stage(server_id, store.STAGE_DURATIONS[stage_index])
    if stage.end <= current_time:
        higher_measure = _finish_stage(stage, current_time)
        if stage_index + 1 < len(store.STAGE_DURATIONS):
            _fill_stage(server_id, stage_index + 1, higher_measure,
                    current_time)

    _add_values(stage, measure)

def _add_values(stage, measure):
    """Adds the measured values to the staging area.
    They will wait there till the stage.end.
    """
    sums = stage.get_sums()
    counts = stage.get_counts()
    for key, increment in measure.sums.iteritems():
        sums[key] = sums.get(key, 0.0) + increment
        counts[key] = counts.get(key, 0) + measure.counts[key]

    stage.update_samples(sums, counts)
    stage.put()

def _finish_stage(stage, current_time):
    """Produces a data point from the collected samples.
    Returns the measured sums and counts used in the point.
    """
    sums = stage.get_sums()
    counts = stage.get_counts()
    measure = _Measure(dict(sums), dict(counts))

    values = stage.get_avg_values()
    if len(values) > 0:
        server_id = stage.get_server_id()
        timestamp = stage.end - stage.get_duration() // 2
        duration = stage.get_duration()
        logging.debug('Creating point at %s: %s', timestamp, values)
        point = Point.prepare(server_id, duration, timestamp, values)
        point.put()

    _clean_stage(stage, current_time)
    return measure

def _clean_stage(stage, current_time):
    """Cleans the stage for next usage.
    """
    duration = stage.get_duration()
    stage.end = _get_next_end(duration, current_time)
    stage.update_samples({}, {})

def _get_next_end(duration, current_time):
    """Returns the nearest future end time for a stage.
    Stage end times are at duration multiples + duration//2.
    Stage middle points are then on whole multiples of the duration.
    """
    # Rounding to the nearest point
    current_time += duration // 2
    nearest_point = current_time - (current_time % duration)
    return nearest_point + duration // 2

def _check_server_secret(agentKey):
    try:
        server_id, secret = Server.split_secret_key(agentKey)
    except ValueError:
        server = None
    else:
        server = Server.get_by_id(server_id)

    if not server or server.secret != secret:
        logging.info("Invalid serverKey: %s", agentKey)
        raise store.NotFoundError("Invalid serverKey: %s" % agentKey)

    return server_id

