#!/bin/bash

VIDEO_DIR=/video

set -e
# Create folders required by nginx upload module
mkdir -p $VIDEO_DIR/nginx_folder/upload/tmp/{0..9}
chmod -R 777 $VIDEO_DIR/nginx_folder
# Create folders for uploaded and converted video
mkdir -p $VIDEO_DIR/{uploads,converted}

/usr/local/nginx/sbin/nginx -c /Video_Compressor_x264ffmpeg/nginx_conf/nginx.conf
python3 /Video_Compressor_x264ffmpeg/big_upl.py
