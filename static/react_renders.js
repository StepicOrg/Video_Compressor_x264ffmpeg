
var UploadForm = React.createClass({

    render: function() {
        return (
            <div></div>
        );
    }
});


var HeaderSectionOne = React.createClass({

    getInitialState: function() {
        return {
            data: "initial"
        };
    },

    render: function(){
        return (
            <div>
                <h1>Here you can convert files for uploading to Stepic.org</h1>
            </div>
        )
    }

});

var HeaderSectionTwo = React.createClass({

    getInitialState: function() {
        return {
            data: "initial"
        };
    },

    render: function(){
        return (
            <div>
                Here is your converted file
            </div>
        )
    }

});

//
//var uploadForm = React.render(
//    <UploadForm />, document.getElementById('upload_form')
//);

//(document.getElementsById('header-one'))

var FooterSection = React.createClass({
   render: function(){
       return (
           <div>
               Made for Stepic.org education engine
           </div>
       )
   }
});

if (document.getElementById('headerMain') != null ) {

    var header = React.render(
        <HeaderSectionOne />, document.getElementById('headerMain')
    );
} else if (document.getElementById('headerSec') != null ) {
        var header = React.render(
        <HeaderSectionTwo />, document.getElementById('headerSec')
    );
}

var footer = React.render(<FooterSection />, document.getElementById('footer'));
