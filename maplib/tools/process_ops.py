import multiprocessing as mp
import threading as td


def multithread(func):
    def wrapper():
        thread = td.Thread(target = func)
        thread.start()
        thread.join()
    return wrapper


def multiprocess(func):
    def wrapper():
        pool = mp.Pool()
        pool.apply_async(func)
        pool.close()
        pool.join()
    return wrapper

