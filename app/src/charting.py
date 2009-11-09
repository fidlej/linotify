
import time

from src import tz, store

GRAPH_COLORS = ('#FF0000', '#0000FF', '#00FF00', '#FF9900',
        '#CC00CC', '#00CCCC', '#33FF00', '#990000', '#000066')

class Chart(object):
    """A chart definition.
    """

    def __init__(self, name, keys, options=None, precision=2):
        """Arguments:
        name - the chart title
        keys - used stats, every key will produce a new graph line
        options - a list of dicts. Each graph line has its own amCharts options.
        precision - a precision to use when formatting the values
        """
        self.name = name
        self.keys = keys
        self.precision = precision
        if options is not None:
            self.options = options
        else:
            self.options = ({},) * len(keys)

        for graph_options, color in zip(self.options, GRAPH_COLORS):
            graph_options['color'] = color
            graph_options['color_hover'] = color

CHARTS = (
        Chart(u'Load averages', ('loadAvrg',)),
        Chart(u'Processes', ('processCnt',), None, precision=0),
        Chart(u'Physical memory',
            ('memUsed', 'memFree', 'memCached', 'memBuffers'),
            ({'balloon_text': 'Used: {value}MB'},
            {'balloon_text': 'Free: {value}MB'},
            {'balloon_text': 'Cached: {value}MB'},
            {'balloon_text': 'Buffers: {value}MB'}), precision=0),
        )

def get_from_to_times():
    now = int(time.time())
    time_from = tz.day_start(now)
    time_to = time_from + tz.DAY_SECONDS
    return time_from, time_to

def generate_timestamps(time_from, time_to):
    duration = _get_usable_duration(time_to - time_from)
    if duration is None:
        duration = stage.STAGE_DURATIONS[-1]
        time_from = time_to - duration * store.LIMIT

    timestamps = []
    t = _round_upto_duration(time_from, duration)
    while t <= time_to:
        timestamps.append(t)
        t += duration
    return timestamps

def get_chart_graphs(server_id, chart, timestamps):
    """Returns a list of (timestamp, value) pairs
    for every key defined in the chart.
    """
    if len(timestamps) < 2:
        return []

    time_from = timestamps[0]
    time_to = timestamps[-1]
    duration = timestamps[1] - time_from

    points = store.get_points(server_id, duration, time_from, time_to)
    graphs = {}
    for key in chart.keys:
        graphs[key] = []

    for point in points:
        timestamp = point.get_timestamp()
        source_values = point.get_values()
        for key in chart.keys:
            value = source_values.get(key)
            if value is not None:
                graphs[key].append((timestamp, value))

    # The lists are returned in a fixed order.
    return [graphs[key] for key in chart.keys]

def _round_upto_duration(timestamp, duration):
    return timestamp + timestamp % duration

def _get_usable_duration(interval):
    for duration in store.STAGE_DURATIONS:
        num_points = interval // duration
        if num_points <= store.LIMIT:
            return duration

    return None

