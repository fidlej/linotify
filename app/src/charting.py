
import time

from src import tz, store

# The maximum number of time points on a chart.
# It should be less than the number of pixels on a chart.
POINTS_LIMIT = 400
assert POINTS_LIMIT <= store.LIMIT - 2  # the -2 is a rounding error

def get_time_range(days, req):
    """Returns start and stop timestamps
    to cover the given number of days.
    """
    now = int(time.time())
    today_end = tz.day_start(now, req) + tz.DAY_SECONDS
    time_from = today_end - days * tz.DAY_SECONDS
    time_to = today_end
    return time_from, time_to

def generate_timestamps(time_from, time_to):
    """Generates time points for the given time range.
    """
    duration = _get_usable_duration(time_to - time_from)
    if duration is None:
        duration = store.STAGE_DURATIONS[-1]
        time_from = time_to - duration * POINTS_LIMIT

    timestamps = []
    t = _floor_to_duration(time_from, duration)
    while t < time_to + duration:
        timestamps.append(t)
        t += duration
    return timestamps

def get_chart_graphs(server_id, chart, timestamps):
    """Returns (key, graph_points) pairs for each graph line.
    A graph point is defined by a (timestamp, value) pair.
    """
    if len(timestamps) < 2:
        return []

    time_from = timestamps[0]
    time_to = timestamps[-1]
    duration = timestamps[1] - time_from

    points = store.get_points(server_id, duration, time_from, time_to)
    graphs = {}
    for point in points:
        timestamp = point.get_timestamp()
        source_values = point.get_values()
        for key, value in source_values.iteritems():
            if key in graphs:
                graphs[key].append((timestamp, value))
            elif chart.is_interesting(key):
                graphs[key] = [(timestamp, value)]

    return chart.tolist(graphs)

def _floor_to_duration(timestamp, duration):
    return timestamp - timestamp % duration

def _get_usable_duration(interval):
    for duration in store.STAGE_DURATIONS:
        num_points = interval // duration
        if num_points <= POINTS_LIMIT:
            return duration

    return None

