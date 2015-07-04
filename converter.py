import pexpect
from settings import DEFAULT_OUT_FILE_SIZE_BYTES
from operations import *
from STATE import GlobalSessionsTable, GlobalRunningTaskTable
import re
import logging

class ConverterTask(object):

    def __init__(self, _source_file, _dest, _socket_obj_set=None, curr=None, _target_size=None):
        if not _target_size:
            self.target_size = DEFAULT_OUT_FILE_SIZE_BYTES
        else:
            self.target_size = _target_size
        self.socket_obj_set = set()
        self.socket_obj_set.add(_socket_obj_set)
        self.source_file = os.path.join(os.path.dirname(__file__), _source_file)
        self.dest = os.path.join(os.path.dirname(__file__), _dest)
        self.data = {'duration': get_length_in_sec(self.source_file), 'bitrate': get_bitrate(self.source_file),
                 'size': get_size(self.source_file), 'all_frames': get_frame_count(self.source_file)}
        self.data['target_bitrate'] = calc_target_bitrate(self.target_size, self.data['duration'])
        # Used in lookup table GlobalSessionsTable
        self.watchers = curr
        self.exitstatus = None
        self.pid = None
        GlobalRunningTaskTable[self.watchers] = self

    def run(self):
        print("Running from ", self.source_file, " to ", self.dest)
        command = (['ffmpeg', '-i', self.source_file, '-c:v', 'libx264', '-strict', '-2', '-crf', '26', '-maxrate', (str(self.data['target_bitrate'])+'k'),
                         '-bufsize', '1835k', self.dest, '-y'])
        thread = pexpect.spawn(' '.join(command))
        self.pid = thread.pid
        print("started %s with pid=%s" % (command, self.pid))
        cpl = thread.compile_pattern_list([pexpect.EOF, "frame= *\d+", '(.+)'])
        while True:
            i = thread.expect_list(cpl, timeout=None)
            if i == 0:
                print("Finished task")
                thread.close()
                self.exitstatus = thread.exitstatus
                break
            elif i == 1:
                frame_number = thread.match.group(0)
                if self.socket_obj_set or GlobalSessionsTable.get(self.watchers):
                    if GlobalSessionsTable.get(self.watchers):
                        self.socket_obj_set = set.copy(GlobalSessionsTable[self.watchers])
                    # Strange behavior here, you can't sent bytes string to sockets?
                    m = re.search(r'frame=.*?(\d+)', frame_number.decode("UTF-8"))
                    if m:
                        int_frame = m.group(1)
                    else:
                        int_frame = "Not Found"
                    if type(self.socket_obj_set) == set:
                        for o in self.socket_obj_set:
                            if o:
                                o.send({'frame': int_frame, 'all_frames': self.data.get('all_frames')})
                    else:
                        self.socket_obj_set.send({'frame': int_frame, 'all_frames': self.data.get('all_frames')})
                # elif GlobalSessionsTable.get(self.watchers):
                #     self.socket_obj = GlobalSessionsTable[self.watchers]
            elif i == 2:
                # ffmpeg output is strange, so we need only 1 line of it
                # unknown_line = thread.match.group(0)
                # print unknown_line
                pass

    def stop_and_delete_original(self):
        try:
            sockjs_conn = GlobalSessionsTable.get(self.watchers)
            if sockjs_conn:
                sockjs_conn.send('done')
                del GlobalSessionsTable[self.watchers]
            os.remove(self.source_file)
        except Exception as e:
            logging.exception("stop_and_delete_original error: %s", e)

    @classmethod
    def stop_by_pid(cls, _id):
        pid = GlobalRunningTaskTable[_id].pid
        stop_process_by_pid(_pid=pid)
