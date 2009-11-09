
import logging

def profiled(fn):
    import cProfile, pstats, StringIO
    prof = cProfile.Profile()
    def wrapper(*args, **kw):
        prof.runctx('wrapper.result = wrapper.fn(*args, **kw)',
                globals(), locals())
        stream = StringIO.StringIO()
        stats = pstats.Stats(prof, stream=stream)
        stats.sort_stats("time")
        stats.print_stats(80)
        # stats.print_callees()
        # stats.print_callers()
        logging.info('Profile data:\n%s', stream.getvalue())
        return wrapper.result

    # To prevent gc the fn
    wrapper.fn = fn
    return wrapper

