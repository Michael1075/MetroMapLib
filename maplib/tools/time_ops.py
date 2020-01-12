import time

import maplib.parameters as params


def timer_decorator(decorator_func=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if decorator_func is None:
                func_name = func.__name__
                new_func = func
            else:
                func_name = " ".join([
                    func.__name__,
                    "by",
                    decorator_func.__name__
                ])
                new_func = decorator_func(func)
            begin = time.time()
            result = new_func(*args, **kwargs)
            end = time.time()
            if params.PRINT_TIMER_MSG:
                print(params.TIMER_MSG.format(func_name, end - begin))
            return result
        return wrapper
    return decorator
