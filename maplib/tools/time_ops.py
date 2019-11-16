import time


def test_time(decorator_func = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal func
            if decorator_func is None:
                func_name = func.__name__
            else:
                func_name = " ".join([
                    func.__name__,
                    "by",
                    decorator_func.__name__
                ])
                func = decorator_func(func)
            begin = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print("Consumed time of function {0}: {1:.3f} second(s)".format(func_name, end - begin))
            return result
        return wrapper
    return decorator

