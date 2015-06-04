import threading
import random
import subprocess, os
from STATE import GlobalSessionsTable

class ConverterQueue(threading.Thread):

    def __init__(self, _queue):
        self.__queue = _queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            task_item = self.__queue.get()
            if task_item is None:
                break
            t = threading.Thread(target=do_convertion, args=(task_item, ))
            t.daemon = True
            t.start()
            self.__queue.task_done()

    def is_empty(self):
        return not self.__queue.unfinished_tasks

def do_convertion(task_item):
    x = random.randint(10,10000)
    print("Converting! ", task_item, x)
    task_item.run()
    print("Watcher Socket:", GlobalSessionsTable[task_item.watchers])
    SocketToWatcher = GlobalSessionsTable[task_item.watchers]
    SocketToWatcher.send("done")
    print("Done ", x)

class ConverterTask(object):

    def __init__(self, _source_file, _dest, curr=None):
        self.source_file = os.path.join(os.path.dirname(__file__), _source_file)
        self.dest = os.path.join(os.path.dirname(__file__), _dest)
        self.watchers = curr

    def run(self):
        print("Running from ", self.source_file, " to ", self.dest)
        subprocess.call(['ffmpeg', '-i', self.source_file, self.dest, '-y'])