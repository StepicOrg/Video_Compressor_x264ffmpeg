

Server for handling multiple async connection and converting files for uploading to Stepic.org.
Uses ffmpeg converter with x264 codec inside.

python3 only

Stack used:<br>
<ul>
<li>nginx, for handling big uploads</li>
<li>tornado, for async workers and websockets</li>
<li>sockjs-tornado, for pushing notification directly</li>
<li>react.js, because it's cool</li>
</ul>

<h2>Installation:</h2>
    brew install nginx-full --with-upload-module
    pip3 install -r requirements.txt


