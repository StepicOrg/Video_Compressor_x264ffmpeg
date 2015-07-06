jQuery(document).ready(function(){
    var _submit = document.getElementById('_submit'),
    _file = document.getElementById('_file'),
    _progress = document.getElementById('_progress');

    var upload = function(){

        if(_file.files.length === 0){
            return;
        }

        var data = new FormData();
        for (var i = 0, f; f = _file.files[i]; i++) {
                data.append('infile', f);
            }

        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            if(request.readyState == 4 && request.status == 200){
                try {
                    //var resp = JSON.parse(request.response);
                    //document.body.innerHTML = request.responseText;
                    var rsp = JSON.parse(request.response);
                    if(rsp.status === "OK"){
                        window.location += 'status/' + rsp.token;
                    }
                    console.log(rsp);
                    //window.location +=
                } catch (e){
                    var resp = {
                        status: 'error',
                        data: 'Unknown error occurred: [' + request.responseText + ']'

                    };
                    window.location += 'error';
                }
                console.log(resp.status + ': ' + resp.data);
            }
        };

        request.upload.addEventListener('progress', function(e){
            _progress.style.width = Math.round(e.loaded * 100 / e.total) + '%';
            //console.log(_progress.style.width);
        }, false);

        request.open('POST', '/upload');
        request.send(data);
    };

    _submit.addEventListener('click', upload);
});