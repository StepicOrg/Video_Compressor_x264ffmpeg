import pexpect
from settings import DEFAULT_OUT_FILE_SIZE_BYTES
from operations import *
from STATE import GlobalSessionsTable

class ConverterTask(object):

    def __init__(self, _source_file, _dest, _socket_obj=None, curr=None, _target_size=None):
        if not _target_size:
            self.target_size = DEFAULT_OUT_FILE_SIZE_BYTES
        else:
            self.target_size = _target_size
        self.socket_obj = _socket_obj
        self.source_file = os.path.join(os.path.dirname(__file__), _source_file)
        self.dest = os.path.join(os.path.dirname(__file__), _dest)
        self.data = {'duration': get_length_in_sec(self.source_file), 'bitrate': get_bitrate(self.source_file),
                     'size': get_size(self.source_file), 'all_frames': get_frame_count(self.source_file)}
        self.data['target_bitrate'] = calc_target_bitrate(self.target_size, self.data['duration'])

        # Used in lookup table GlobalSessionsTable
        self.watchers = curr

    def run(self):
        print("Running from ", self.source_file, " to ", self.dest)
        command = (['ffmpeg', '-i', self.source_file, '-c:v', 'libx264', '-strict', '-2', '-crf', '26', '-maxrate', (str(self.data['target_bitrate'])+'k'),
                         '-bufsize', '1835k', self.dest, '-y'])
        # result = subprocess.Popen(command,stdout=subprocess.PIPE)
        thread = pexpect.spawn(' '.join(command))
        print("started %s" % command)
        cpl = thread.compile_pattern_list([pexpect.EOF, "frame= *\d+", '(.+)'])
        while True:
            i = thread.expect_list(cpl, timeout=None)
            if i == 0:
                print("Finished task")
                thread.close()
                break
            elif i == 1:
                frame_number = thread.match.group(0)
                if self.socket_obj:
                    # Strange behavior here, you can't sent bytes string to sockets?
                    int_frame = int(frame_number.decode("UTF-8").split(' ')[-1])
                    self.socket_obj.send({'frame': int_frame, 'all_frames': self.data.get('all_frames')})
                elif GlobalSessionsTable.get(self.watchers):
                    self.socket_obj = GlobalSessionsTable[self.watchers]
            elif i == 2:
                # ffmpeg output is strange, so we need only 1 line of it
                # unknown_line = thread.match.group(0)
                # print unknown_line
                pass

