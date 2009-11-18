"""
Chart definitions.
"""

GRAPH_COLORS = ('#FF0000', '#0000FF', '#00FF00', '#FF9900',
        '#CC00CC', '#00CCCC', '#99CC00', '#990000', '#000066')

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
    def __init__(self, name, key_options, precision=2):
        """Arguments:
        name - the chart title
        key_options - a list of (key, options) pairs.
            The order of the keys is used to order the graphs.
        precision - a precision to use when formatting the values
        """
        self.name = name
        self.keys = [key for key, options in key_options]
        self.multi_options = [options for key, options in key_options]
        self.precision = precision

        for i, graph_options in enumerate(self.multi_options):
            graph_options.update(_get_base_options(i))

    def is_interesting(self, key):
        return key in self.keys

    def get_options(self, graph_index, key):
        return self.multi_options[graph_index]

    def tolist(self, graphs):
        """Uses the order of the specified keys.
        """
        return [(key, graphs.get(key, ())) for key in self.keys]


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
        FixedChart(u'Load averages',
            [('loadAvrg', {'balloon_text': u'{value} processes awake'})]),
        FixedChart(u'Processes',
            [('processCnt', {'balloon_text': u'{value} processes'})],
            precision=0),
        FixedChart(u'Physical memory',
            [
                ('memUsed', {'balloon_text': u'Used: {value}MB'}),
                ('memFree', {'balloon_text': u'Cached: {value}MB'}),
                ('memCached', {'balloon_text': u'Free: {value}MB'}),
                ('memBuffers', {'balloon_text': u'Buffers: {value}MB'}),
                ('swapUsed', {'balloon_text': u'Used swap: {value}MB'}),
            ], precision=0),
        DynamicChart(u'Disk usage', 'disk ',
            {'balloon_text': u'${key_tail} {value}% used'})
        )

