import threading
import subprocess, os
from settings import MAX_WORKERS

class ConverterQueue(threading.Thread):

    WORKERS = 0
    converter_func_obj = None

    def __init__(self, _queue, _converter_func_obj):
        self.__queue = _queue
        self.converter_func_obj = _converter_func_obj
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if self.WORKERS <= MAX_WORKERS :
                task_item = self.__queue.get()
                if task_item is None:
                    break

                t = threading.Thread(target=self.converter_func_obj, args=(task_item, ))
                t.daemon = True
                self.WORKERS += 1
                t.start()
                self.__queue.task_done()

    def is_empty(self):
        return not self.__queue.unfinished_tasks

class ConverterTask(object):

    def __init__(self, _source_file, _dest, curr=None):
        self.source_file = os.path.join(os.path.dirname(__file__), _source_file)
        self.dest = os.path.join(os.path.dirname(__file__), _dest)
        self.watchers = curr

    def run(self):
        print("Running from ", self.source_file, " to ", self.dest)
        subprocess.call(['ffmpeg', '-i', self.source_file, self.dest, '-y'])