import gevent.monkey
gevent.monkey.patch_all()

import gevent.pool
import gevent.queue
from greenlet import greenlet
import logging as log


def green_producer(iterator, map_func, queue, consumer_instance, pool_size,
                   consumer_args=(), consumer_kwargs={}):
    """A map function:

    Map pool.spawn(func, iterated_element) on iterator
    until the gevent pool is full or the iterator is exhausted.

    Put the return value (a gevent.event.AsyncResult) of each spawned func call
    into the queue.

    Whenever the pool is full, switch control to the consumer_instance greenlet.

    When control switches back to this instance, fill up pool again.
    """
    log.debug('initializing producer.  This will only appear once per greenlet')
    consumer_instance.switch(*consumer_args, **consumer_kwargs)
    pool = gevent.pool.Pool(7)
    for elem in iterator:
        log.debug("Queued job for elem {elem}".format(**locals()))
        queue.put(pool.spawn(map_func, elem))
        if pool.full():
            consumer_instance.switch()
    gevent.joinall(pool)


def green_consumer_sink(sink_func, queue, producer_instance):
    """
    Consume queue if anything is immediately available and apply sink_func
    to return value of each consumed item.
    If nothing is immediately available, switch to producer_instance greenlet.

    Details:
    Call queue.get_nowait(), and expect to receive a gevent.event.AsyncResult.
    Then, apply sink_func(async_result.get())
    If nothing is immediately available, switch to producer_instance greenlet.

    For cases where sink_func requires the same costly initialization every call,
    consider a coroutine sink_func:
        sink_func = lambda rv:other_func.send(rv)
    """
    log.debug('initializing consumer.  This will only appear once per greenlet')
    producer_instance.switch()

    while True:
        try:
            async_result = queue.get_nowait()
        except gevent.queue.Empty:
            producer_instance.switch()
        try:
            rv = async_result.get()
        except Exception, e:
            log.exception(e)
            producer_instance.switch()
        sink_rv = sink_func(rv)
        log.debug("Completed job with sink result: {sink_rv}".format(**locals()))


def main(iterator, map_func, sink_func, pool_size):
    """Execute green_producer and green_consumer together"""
    queue = gevent.queue.Queue()
    producer_instance = greenlet(green_producer)
    consumer_instance = greenlet(green_consumer_sink)
    consumer_args = (sink_func, queue, producer_instance)

    # Initialize each greenlet and assume that it will immediately
    # return control back
    producer_instance.switch(
        iterator, map_func, queue, consumer_instance, pool_size,
        consumer_args)
    consumer_instance.switch()


if __name__ == '__main__':
    log.root.setLevel(1)
    iterator = xrange(10)
    map_func = lambda x: x ** 2
    sink_func = lambda x: 'Sink got %d' % x
    pool_size = 1
    main(iterator, map_func, sink_func, pool_size)
