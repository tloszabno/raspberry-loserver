import time
from threading import Thread


def timed(func):
    def func_wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        print(
            "Function %s took %s sec" % (str(func.__name__), str(end - start)))
        return r
    return func_wrapper


def avg(l):
    l = [x for x in l if x]  # filter NoneTypes
    return sum(l) / float(len(l))


def execute_async(action):
    t = Thread(target=action)
    t.daemon = True
    t.start()
