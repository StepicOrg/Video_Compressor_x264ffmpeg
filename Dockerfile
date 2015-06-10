FROM centos:centos7
MAINTAINER mehanig <mehanig@gmail.com>

RUN yum install -y http://dl.iuscommunity.org/pub/ius/stable/CentOS/7/x86_64/ius-release-1.0-14.ius.centos7.noarch.rpm \
 && yum install -y python34u \
 && yum install -y git \
 && yum clean all

RUN git clone https://github.com/mehanig/Video_Compressor_x264ffmpeg
RUN cd Video_Compressor_x264ffmpeg \
  && pip3 install -r requirements.txt
RUN yum install -y nginx
RUN nginx -c ~/Video_Compressor_x264ffmpeg/nginx_conf/nginx.conf
RUN python3 Video_Compressor_x264ffmpeg/big_upl.py
