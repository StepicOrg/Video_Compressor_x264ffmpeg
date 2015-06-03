import threading
import queue as Queue
import time, random

class ConverterQueue(threading.Thread):

    def __init__(self, queue):
        self.__queue = queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            item = self.__queue.get()
            if item is None:
                break
            t = threading.Thread(target=do_convertion, args=(item, ))
            t.daemon = True
            t.start()
            self.__queue.task_done()

            time.sleep(random.randint(10, 100) / 1000.0)

    def is_empty(self):
        return not self.__queue.unfinished_tasks
            # print("task", item, "finished")

def do_convertion(item):
    x = random.randint(10,10000)
    print("Converting! ", item, x)
    time.sleep(random.randint(1000, 5000) / 1000.0)
    print("Done ", x)