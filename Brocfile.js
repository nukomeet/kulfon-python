var concat = require('broccoli-concat'),
    funnel = require('broccoli-funnel'),
    sass = require('broccoli-sass-source-maps'),
    rev = require('broccoli-asset-rev'),
    merge = require('broccoli-merge-trees');

var babel = require('broccoli-babel-transpiler');
var browserify = require('broccolify');
var cssnano = require('broccoli-cssnano');
var uglify = require('broccoli-uglify-js');
var env = require('broccoli-env').getEnv();

var img = funnel('images', {
  destDir: 'assets'
})

var js = babel('javascripts', {});

var bower = 'bower_components'

js = browserify(merge([bower, js]), {
  entries: ['./main.js'],
  // require: [['./skrollr/src/skrollr.js', {expose: 'skrollr'}]],
  outputFile: 'assets/main.js'
  // browserify: {
  //   debug: true
  // }
});

var css = sass(['stylesheets',
                'bower_components/bourbon/app/assets/stylesheets',
                'bower_components/neat/app/assets/stylesheets',
                'bower_components/bitters/app/assets/stylesheets'
               ],
               'main.scss',
               'assets/styles.css',
               {});

var html = 'public'

var result;

switch(env) {
  case 'development':
    result = merge([js, css, img, html]);
  break;
  case 'production':
    css = cssnano(css);
    js = uglify(js);
    result = rev(merge([js, css, img, html]));
  break;
}

module.exports = result;