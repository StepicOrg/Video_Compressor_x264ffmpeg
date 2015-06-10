

Server for handling multiple async connection and converting files for uploading to Stepic.org.
Uses ffmpeg converter with x264 codec inside.

python3 only

Stack used:<br>
<ul>
<li>Packed inside Docker container</li>
<li>nginx, for handling big uploads</li>
<li>tornado, for async workers and websockets</li>
<li>sockjs-tornado, for pushing notification directly</li>
<li>react.js, because it's cool</li>
</ul>

<h2>OSX Deployment:</h2>
    install boot2docker
    docker build -t video_compressor .
    docker run -it -rm -p 8080:8080 -p 8084:8084 -t video_compressor


