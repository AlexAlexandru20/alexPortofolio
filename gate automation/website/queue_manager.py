import multiprocessing

queue = None

def get_queue():
    global queue
    if queue is None:
        queue = multiprocessing.Queue()

    return queue