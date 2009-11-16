
import time

from src import tz, store

GRAPH_COLORS = ('#FF0000', '#0000FF', '#00FF00', '#FF9900',
        '#CC00CC', '#00CCCC', '#33FF00', '#990000', '#000066')

class Chart(object):
    """A chart definition.
    A chart could have multiple graphs.
    A graph displays points stored under a key.
    """
    precision = 2
    name = ''

    def is_interesting(self, key):
        """Returns true if the chart should have
        a graph for the given key.
        """
        return False

    def get_options(self, graph_index, key):
        """Returns amCharts attributes for the specified graph.
        """
        return {}

    def tolist(self, graphs):
        """Converts the dict of graphs
        to a list of (key, graph) pairs with a fixed order.
        """
        raise NotImplementedError


def _get_base_options(graph_index):
    options = {}
    color = GRAPH_COLORS[graph_index % len(GRAPH_COLORS)]
    options['color'] = color
    options['color_hover'] = color
    return options

class FixedChart(Chart):
    """A chart with a fixed list of keys.
    """
    def __init__(self, name, keys, multi_options=None, precision=2):
        """Arguments:
        name - the chart title
        keys - used stats, every key will produce a new graph
        multi_options - a list of dicts.
            Each graph has its own amCharts options.
        precision - a precision to use when formatting the values
        """
        self.name = name
        self.keys = keys
        self.precision = precision
        if multi_options is not None:
            self.multi_options = multi_options
        else:
            self.multi_options = ({},) * len(keys)

        for i, graph_options in enumerate(self.multi_options):
            graph_options.update(_get_base_options(i))

    def is_interesting(self, key):
        return key in self.keys

    def get_options(self, graph_index, key):
        return self.multi_options[graph_index]

    def tolist(self, graphs):
        """Uses the order of the specified keys.
        """
        return [(key, graphs[key]) for key in self.keys]


class DynamicChart(Chart):
    def __init__(self, name, key_prefix, options=None):
        self.name = name
        self.key_prefix = key_prefix
        self.options = options

    def is_interesting(self, key):
        return key.startswith(self.key_prefix)

    def get_options(self, graph_index, key):
        graph_options = dict(_get_base_options(graph_index))
        graph_options.update(self.options)
        key_tail = key[len(self.key_prefix):]
        for key, value in graph_options.iteritems():
            graph_options[key] = value.replace('${key_tail}', key_tail)
        return graph_options

    def tolist(self, graphs):
        """Sorts the graphs by their key.
        """
        items = graphs.items()
        items.sort()
        return items

CHARTS = (
        FixedChart(u'Load averages', ('loadAvrg',)),
        FixedChart(u'Processes', ('processCnt',), None, precision=0),
        FixedChart(u'Physical memory',
            ('memUsed', 'memFree', 'memCached', 'memBuffers'),
            ({'balloon_text': u'Used: {value}MB'},
            {'balloon_text': u'Free: {value}MB'},
            {'balloon_text': u'Cached: {value}MB'},
            {'balloon_text': u'Buffers: {value}MB'}), precision=0),
        DynamicChart(u'Disk usage', 'disk ',
            {'balloon_text': u'${key_tail} {value}% used'})
        )

def get_time_range(days):
    """Returns start and stop timestamps
    to cover the given number of days.
    """
    now = int(time.time())
    today_end = tz.day_start(now) + tz.DAY_SECONDS
    time_from = today_end - days * tz.DAY_SECONDS
    time_to = today_end
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

def _round_upto_duration(timestamp, duration):
    return timestamp + timestamp % duration

def _get_usable_duration(interval):
    for duration in store.STAGE_DURATIONS:
        num_points = interval // duration
        if num_points <= store.LIMIT:
            return duration

    return None

