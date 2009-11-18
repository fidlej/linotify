
from nose.tools import assert_equal, assert_not_equal
from src import chartdef

def test_fixed_chart():
    chart = chartdef.FixedChart(u'A chart',
            (
                ('key1', {'option1':'o1', 'option2':'o2'}),
                ('key2', {'option1':'key2_o1', 'option2':'key2_o2'})
            ))

    assert_equal(chart.is_interesting('key1'), True)
    assert_equal(chart.is_interesting('key_x'), False)
    assert_equal(chart.get_options(0, 'key1')['option1'], 'o1')

