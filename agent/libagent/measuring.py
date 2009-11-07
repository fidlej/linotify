
def measure_stats():
    return {
            'loadAvrg': _measure_load(),
            'processCnt': _measure_num_processes(),
            }

def _measure_load():
    loadavg = open('/proc/loadavg').readline()
    over5minutes = float(loadavg.split()[1])
    return over5minutes

def _measure_num_processes():
    output = _capture('ps', 'ax')
    return len(output.splitlines()) - 1

def _capture(*args):
    import subprocess
    process = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)
    return process.communicate()[0]

