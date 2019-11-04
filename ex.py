import multiprocessing as mp

from tools.time_ops import test_time


CONST = 1000000


def job(x):
    return x ** 2


@test_time
def normal():
    res = list(map(job, range(CONST)))
    print(res[-10:])


@test_time
def multicore():
    pool = mp.Pool()
    res = pool.map(job, range(CONST))
    print(res[-10:])


if __name__ == '__main__':
    normal()
    multicore()

