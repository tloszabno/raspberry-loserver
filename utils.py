import time


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
    sum(l) / float(len(l))
