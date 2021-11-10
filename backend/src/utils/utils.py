import time
import logging

LOGGING_TIMING_LEVEL_NUM = 42
logging.addLevelName(LOGGING_TIMING_LEVEL_NUM, "TIMING")


def logging_timing_level(message, *args, **kwargs):
    logging.Logger._log(logging.root, LOGGING_TIMING_LEVEL_NUM, message, args, **kwargs)


logging.timing = logging_timing_level


def timeit(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        logging.timing(f"{func.__name__!r} executed in {(time.time()-t1):.3f}s")
        return result

    return wrapper