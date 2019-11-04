import time


def test_time(func):
    def wrapper(*args, **kwargs):
        begin = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Consumed time of function {0}: {1:.3f} second(s)".format(func.__name__, end - begin))
        return result
    return wrapper

