
def measure_stats():
    stats = {}
    sources = [_measure_load, _measure_num_processes, _measure_mem]
    for source in sources:
        sub_stats = source()
        stats.update(sub_stats)

    return stats

def _capture(*args):
    import subprocess
    process = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)
    return process.communicate()[0]

def _measure_load():
    loadavg = open('/proc/loadavg').readline()
    over5minutes = float(loadavg.split()[1])
    return {'loadAvrg': over5minutes}

def _measure_num_processes():
    output = _capture('ps', 'ax')
    return {'processCnt': len(output.splitlines()) - 1}


def _measure_mem():
    meminfo = {}
    for line in open('/proc/meminfo'):
        name, value = line.split(':', 1)
        value = value.strip()
        if value.endswith(' kB'):
            value = value.replace(' kB', '')
            value = int(value) >> 10
            meminfo[name] = value

    stats = {}
    stats['memFree'] = meminfo['MemFree']
    stats['memBuffers'] = meminfo['Buffers']
    stats['memCached'] = meminfo['Cached']
    stats['memUsed'] = meminfo['MemTotal'] - meminfo['MemFree']
    return stats

