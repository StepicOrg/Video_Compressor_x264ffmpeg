module.exports = function (grunt) {

    require("load-grunt-tasks")(grunt); // npm install --save-dev load-grunt-tasks

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: 'src/<%= pkg.name %>.js',
                dest: 'build/<%= pkg.name %>.min.js'
            }
        },
        "babel": {
            options: {
                sourceMap: true
            },

            dist: {
                files:[ {
                    "expand":true,
                    "cwd": "static/",
                    "src":["*.js"],
                    "dest": "build/",
                    "ext":".js"
                }]
            }
        }
    });

    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-babel');
    // Default task(s).
    //grunt.registerTask('default', ['uglify']);
    grunt.registerTask("default", ["babel"]);
};