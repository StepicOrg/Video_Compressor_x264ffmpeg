__author__ = 'mehanig'
import subprocess
import os
import signal
from settings import FFPROBE_RUN_PATH

'''
Possible problems might cause if filename contains "Duration" and other keywords
'''

def get_length_in_sec(filename: str) -> int:
    result = subprocess.Popen([FFPROBE_RUN_PATH, filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration_string = [x.decode("utf-8") for x in result.stdout.readlines() if "Duration" in x.decode('utf-8')][-1]
    time = duration_string.replace(' ', '').split(',')[0].replace('Duration:', '').split(':')
    return int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2].split('.')[0])

def get_bitrate_from_ffprobe(filename: str) -> int:
    result = subprocess.Popen([FFPROBE_RUN_PATH, filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration_string = [x.decode("utf-8") for x in result.stdout.readlines() if "Duration" in x.decode('utf-8')][-1]
    bitrate = duration_string.split(',')[-1].replace(' bitrate: ', '').split(' ')[0]
    return int(bitrate)

def get_size(filename: str) -> int:
    return os.path.getsize(filename)

def get_bitrate(filename: str) -> int:
    return int((get_size(filename)*8)/(1024*get_length_in_sec(filename)))

def calc_target_bitrate(byte_size: int, length_sec: int) -> int:
    return int((byte_size*8)/(1024*length_sec))

def get_frame_count(filename: str) -> int:
    result = subprocess.Popen([FFPROBE_RUN_PATH, '-select_streams', 'v', '-show_streams', filename],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    frames = [x.decode("utf-8") for x in result.stdout.readlines() if "nb_frames=" in x.decode('utf-8')][0]
    return int(frames.split('=')[-1])

def stop_process_by_pid(_pid):
    os.kill(_pid, signal.SIGKILL)

if __name__ == '__main__':
    print(get_size('/Users/mehanig/Documents/MultTreadWorker.mp4'))
    print(get_bitrate('/Users/mehanig/Documents/MultTreadWorker.mp4'))
    print(get_bitrate_from_ffprobe('/Users/mehanig/Documents/MultTreadWorker.mp4'))
    print(get_length_in_sec('/Users/mehanig/Documents/MultTreadWorker.mp4'))
    print(calc_target_bitrate(3579947, 22))
    print(get_frame_count('/Users/mehanig/Documents/MultTreadWorker.mp4'))