
import logging

def measure_stats():
    stats = {}
    sources = (
            _measure_load,
            _measure_num_processes,
            _measure_mem,
            _measure_disk_usage,
            )
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
    """Counts the number of running processes
    based on the number of /proc/PID entries.
    """
    import os
    count = 0
    filenames = os.listdir('/proc')
    for filename in filenames:
        # GNU ps does the same detection
        if '0' < filename[0] <= '9':
            count += 1

    return {'processCnt': count}

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
    stats['swapFree'] = meminfo['SwapFree']
    stats['swapUsed'] = meminfo['SwapTotal'] - meminfo['SwapFree']
    return stats

INDEX_DISK = 0
INDEX_PERCENT = 4
INDEX_MOUNT_POINT = 5

def _measure_disk_usage():
    output = _capture('df', '-P', '-k')
    stats = {}
    lines = output.splitlines()[1:]
    for line in lines:
        parts = line.split()
        if len(parts) < INDEX_PERCENT:
            continue

        percent = parts[INDEX_PERCENT]
        if not percent.endswith('%'):
            logging.info('A disk without size: %r', line)
            continue

        percent = int(percent[:-1])

        if len(parts) > INDEX_MOUNT_POINT:
            key = 'disk %s (%s)' % (parts[INDEX_DISK], parts[INDEX_MOUNT_POINT])
        else:
            key = 'disk %s' % parts[INDEX_DISK]
        stats[key] = percent

    return stats

