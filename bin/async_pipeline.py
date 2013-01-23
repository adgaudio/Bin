"""Some implementations for running async code with gevent I made while
learning how to use the library.

These are, in my opinion, over-engineered and poor examples of greenlet-based
concurrency.  A simple futures model using gevent's AsyncResult would remove
most of the complication.

However, this file has some interesting ideas worth investigating.

All functions work reliably as described.
"""
import gevent
import gevent.pool
import gevent.queue
import gevent.monkey
gevent.monkey.patch_all(thread=False)

from log import log


def chunk(size, iterable):
    iterable = iter(iterable)
    while True:
        loop = [elem for elem, _ in zip(iterable, range(size))]
        if not loop:
            break
        yield loop


class MutableInt(object):
    def __init__(self, start_val):
        self.num = [start_val]

    def inc(self):
        self.num.append(self.num.pop() + 1)

    def dec(self):
        self.num.append(self.num.pop() - 1)

    def get(self):
        return self.num[-1]


def _job_spawner(func, seq, queue, pool, link_value_func, link_exception_func):
    """Generator that populates queue with output from func(args)
    for args in seq.  Calls link_value_func() when successful
    and link_exception_func() when error raised
    """
    for args in seq:
        job = pool.spawn(lambda args: queue.put((args, func(args))), args)
        job.link_value(link_value_func)
        job.link_exception(link_exception_func)
        yield job


def mapf(func, seq, block, pool_size):
    """Map function onto sequence
    Return queue containing (args, func(args)) tuples

    If block, the number of jobs must be able to fit in memory
    If not block, jobs aren't spawned until they are interated through
    """
    num_successes = MutableInt(0)
    queue = gevent.queue.Queue()
    pool = gevent.pool.Pool(pool_size)
    job_spawner = _job_spawner(func, seq, queue, pool,
                               lambda g: num_successes.inc(),
                               lambda g: log.error('whoa! greenlet failed: %s' % g.exception))
    if block:
        job_spawner = list(job_spawner)
        gevent.joinall(job_spawner)
    return queue, job_spawner, num_successes


def group_reduce(func, queue, timeout, group_size=2):
    """Chunk queue into given group_size, and map func onto the seq of chunks
    queue.get(timeout=timeout) returns data of form (ID, args) if the
    queue returns data quickly enough, otherwise function quits.

    Because this func consumes the queue, it decrements mutable_qsize.
    If timeout is 0, this function will block until queue is not empty"""
    while True:
        group = []
        try:
            for _ in range(group_size):
                group.append(queue.get(timeout=timeout))
        except gevent.queue.Empty:
            [queue.put(elem) for elem in group]
            break
        ids = tuple(x[0] for x in group)
        rv = func(*(x[1] for x in group))
        yield (ids, rv)


def map_reduce_queue(mapper, reducer, seq, num_reducer_args,
                     block, timeout, chunk_size):
    """
    Essentially, reduce(reducer, map(mapper, seq))
    where reducer takes num_reducer_args and mapper is asynchronous

    Details:
        Map mapper func on seq asynchronously using gevent, and ignore exceptions
        Then, iteratively:
        Start chunk_size jobs, which write mapper output to a queue.
        Every chunk_size jobs, continue to yield this tuple until queue is empty:
             (num_reducer_args mapper args, reducer(num_reducer_args of mapper outputs))
        After mapper consumes queue, execute previous step with given timeout

    A good estimate for chunk_size might be:
        chunk_size >= (num_reducer_args) * (1 + percent expected mapper failures)

    Runtime notes: Guarantee no deadlocks.  However, because this func is a
    generator, it may be partially io-bound if it is not allowed to yield
    quickly enough (and the mapf pool_size is too small)
    """
    n_yields = 0
    queue, jobs, num_successes = mapf(mapper, seq, block, 5 * chunk_size)
    for _ in chunk(chunk_size, jobs):  # starts jobs that write to queue
        for rv in group_reduce(reducer, queue,  # consumes queue
                               timeout=0, group_size=num_reducer_args):
            n_yields += 1
            yield rv
        gevent.sleep(0)
    for rv in group_reduce(reducer, queue,
                           timeout=timeout, group_size=num_reducer_args):
        n_yields += 1
        yield rv
    if num_successes.get() == n_yields:
        msg = """num_tagged_urls: %s  ncrawled_urls:%s""" % (
            n_yields, num_successes.get())
        gevent.sleep(5)
        msg += '  ncrawed_urls a few secs later: %s' % num_successes.get()
        log.error(msg)


def main(*args, **kwargs):
    return map_reduce_queue(*args, **kwargs)
