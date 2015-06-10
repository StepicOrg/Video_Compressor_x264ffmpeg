import threading
import os
from settings import MAX_WORKERS, DEFAULT_OUT_FILE_SIZE_BYTES
from operations import *
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

    def __init__(self, _source_file, _dest, curr=None, _target_size=None):
        if not _target_size:
            self.target_size = DEFAULT_OUT_FILE_SIZE_BYTES
        else:
            self.target_size = _target_size
        self.source_file = os.path.join(os.path.dirname(__file__), _source_file)
        self.dest = os.path.join(os.path.dirname(__file__), _dest)
        self.data = {'duration': get_length_in_sec(self.source_file), 'bitrate': get_bitrate(self.source_file),
                     'size': get_size(self.source_file)}
        self.data['target_bitrate'] = calc_target_bitrate(self.target_size, self.data['duration'])

        #Used in lookup table GlobalSessionsTable
        self.watchers = curr

    def run(self):
        print("Running from ", self.source_file, " to ", self.dest)
        command = (['ffmpeg', '-i', self.source_file, '-c:v', 'libx264', '-crf', '26', '-maxrate', (str(self.data['target_bitrate'])+'k'),
                         '-bufsize', '1835k', self.dest, '-y'])
        print(command)
        subprocess.Popen(command)