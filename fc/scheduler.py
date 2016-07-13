# standard library
import logging
import queue
import time

logger = logging.getLogger()

def process_queue(q, pool, func):
    """ Process a priority queue based on time

    The priority within the queue is the time at which the item can execute.

    Continually poll the queue, popping an item only when the current time
    is greater than the time at which the item is permitted to execute.  The
    queue is designed in this manner in order to deal with API rate limiting.

    Parameters
    ----------
    q : an instance of a priority queue

    pool : a thread pool

    func : the function to be executed by a thread in the threadpool

    Returns
    -------
    null
    """
    # import global
    from fc import (QUEUE_TIMEOUT,
                    TEST_FLAG)

    # get first item in the queue
    priority, count, id_val, dt, email = q.get()

    # loop through until the queue is empty for __ seconds
    while True:
        diff = priority - time.time()
        # if we have crossed the timing threshold
        if diff <= 0:
            logger.info(('Submit | email: {_email}  id: {_id}'
                         ' | submit {_email} for execution')
                         .format(_email=email, _id=id_val))

            if TEST_FLAG:
                # submit to print_email - useful for testing
                a = pool.submit(func, email)
            else:
                # submit to process_one_email
                a = pool.submit(func, q, count, id_val, dt, email)

            try:
                priority, count, id_val, dt, \
                        email = q.get(timeout=QUEUE_TIMEOUT)
            except queue.Empty:
                break

        # sliding scale for sleeping
        # based on an idea from the pause package
        # https://pypi.python.org/pypi/pause
        if diff <= 0.1:
            time.sleep(0.001)
        elif diff <= 0.5:
            time.sleep(0.01)
        elif diff <= 1.5:
            time.sleep(0.1)
        else:
            time.sleep(1)
