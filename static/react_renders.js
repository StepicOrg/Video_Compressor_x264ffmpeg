/** @jsx React.DOM */

var UploadForm = React.createClass({

    getInitialState: function(){
        return {
            data: this.props.data,
            substep_list: this.props.substep_list
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({
              data: nextProps,
              substep_list: nextProps.substep_list
          });
    },

    render: function() {
        return (
          <div className="uploadForm">
             ImUploadForm
          </div>
        );
    }
});



var uploadForm = React.render(
    <UploadForm />, document.getElementById('upload_form')
);