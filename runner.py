import threading
import multiprocessing as mp
import time
from sady.gateway import Worker


def foo_pool(x):
    time.sleep(2)
    print "go"
    return x * x


result_list = []


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    # result_list.append(result)
    print result


def apply_async_with_callback():
    pool = mp.Pool()
    for i in range(2):
        pool.apply_async(foo_pool, args=(i,), callback=log_result)
    pool.close()
    pool.join()
    print(result_list)


def done(tid, tgroup, *args):
    print "DONE"

if __name__ == '__main__':
    print "crate worker"
    w = Worker(1, "--", apply_async_with_callback, done)
    w.start()
    print "done__"

