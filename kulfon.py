import click

from glob import glob
from os.path import join, dirname
from subprocess import call

import json
import sys
import os
import colorama
import errno
import shutil
import yaml
import sass
import time
import hashlib
import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from jinja2 import Environment, FileSystemLoader

from webassets import Environment as AssetsEnvironment
from webassets import Bundle
from webassets.ext.jinja2 import AssetsExtension
from webassets.script import CommandLineEnvironment

import SimpleHTTPServer
import SocketServer


BASE_HTML="""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{% block title %}Welcome to Kulfon{% endblock %}</title>
  <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">

  <link href="/assets/styles.css" rel="stylesheet">

  {% block head %}{% endblock %}
</head>
<body>
  {% block content %}{% endblock %}

  {% assets "app" %}
  <script type="text/javascript" src="{{ ASSET_URL }}"></script>
  {% endassets %}
</body>
</html>
"""[1:-1]

INDEX_HTML="""
{% extends "layouts/base.html" %}

{% block content %}
<h1>Hello, {{ data['name'] }}, I'm Kulfon</h1>
{% endblock %}
"""[1:-1]

STYLES_SCSS="""
body {
    color: red;
}
"""[1:-1]

DATA_YML="""
name: My Friend
"""

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

imports = []
vendor = []
for f in glob(join('bower_components', '*', 'bower.json')):
    with open(f) as content:
        bower_json = json.load(content)
        imports.append(join('bower_components', bower_json['name'], dirname(bower_json['main'])))

        _, ext = os.path.splitext(bower_json['main'])
        if ext == '.js':
            vendor.append(join('bower_components', bower_json['name'], bower_json['main']))

assets_env = AssetsEnvironment(directory='.', url='/assets')
assets_env.versions = 'hash:32' 

# TODO it doesn't work
assets_env.config['closure_compressor_optimization'] = 'WHITESPACE_ONLY'

vendor = Bundle(*vendor, output='dist/assets/vendor.%(version)s.js', filters='rjsmin')
main = Bundle('javascripts/main.js', output='dist/assets/app.%(version)s.js', filters='rjsmin')

app = Bundle(vendor, main)

assets_env.register('app', app)


class MyHandler(PatternMatchingEventHandler):
    def on_modified(self, event):
        load_data()
        print event

        _, ext = os.path.splitext(event.src_path)
        switcher = {
            '.scss': css,
            '.js': js,
            '.html': render,
        }
        click.echo('Recompiling %s' % ext)
        switcher.get(ext, lambda: None)()

event_handler = MyHandler(patterns=['*.scss', '*.js', '*.html'])
observer = Observer()

PORT = 5002

def load_data():
    with open("data.yml", 'r') as stream:
        global data
        data = yaml.load(stream)

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def fill(fname, content):
    with open(fname, 'w') as file:
        file.write(content)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def is_partial(filename):
    return os.path.dirname(filename).startswith('partials') 

def is_layout(filename):
    return os.path.dirname(filename).startswith('layouts') 

def is_ignored(filename):
    return any((x.startswith(".") for x in filename.split(os.path.sep)))

def is_nonhtml(filename):
    return os.path.splitext(os.path.basename(filename))[1] != '.html'

def is_template(filename):
    if is_partial(filename):
        return False

    if is_ignored(filename):
        return False

    if is_nonhtml(filename):
        return False

    if is_layout(filename):
        return False

    return True

def render(extensions=[], stylesheets=None, target='development'):
    env = Environment(
        loader=FileSystemLoader('./views'),
        extensions=extensions,
        keep_trailing_newline=True,
    )
    env.assets_environment = assets_env

    javascripts = [os.path.basename(path) for path in assets_env['app'].urls()]

    for t in env.list_templates(filter_func=is_template):
        template = env.get_template(t)
        if template.name == 'index.html':
            filepath = 'index.html'
        else:
            filepath = os.path.join(os.path.splitext(template.name)[0], 'index.html')

        mkdir_p(os.path.join('./dist', os.path.dirname(filepath)))

        template.stream({
            'data': data, 
            'stylesheets': stylesheets,
            'javascripts': javascripts
        }).dump(os.path.join('./dist', filepath), "utf-8")



@click.group()
def cli():
    pass

@cli.command()
def clean():
    shutil.rmtree('dist/', ignore_errors=True)

def setup():
    mkdir_p('dist/assets')

def css(target='development'):
    content = sass.compile(
        filename='stylesheets/styles.scss',
        output_style='nested' if target == 'development' else 'compressed',
        include_paths=imports
    )

    if target == 'production':
        version = hashlib.md5(content).hexdigest()
        output_name = 'dist/assets/styles.{}.css'.format(version)
    else:
        output_name = 'dist/assets/styles.css'

    with open(output_name, 'w') as fout:
        fout.write(content)

    return os.path.basename(output_name)

def js():
    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.WARNING)

    cmdenv = CommandLineEnvironment(assets_env, log)
    cmdenv.build()

def images():
    os.system("rsync -az images/ dist/assets")

@cli.command()
@click.argument('directory', type=click.Path(file_okay=False), default='.')
def init(directory):
    """Initialize `kulfon` directory structure; default is `.`, i.e. 
    current directory.
    """
    mkdir_p(join(directory, 'javascripts'))
    mkdir_p(join(directory, 'stylesheets'))
    mkdir_p(join(directory, 'images'))
    mkdir_p(join(directory, 'views', 'layouts'))
    mkdir_p(join(directory, 'views', 'partials'))

    fill(join(directory, 'stylesheets', 'styles.scss'), STYLES_SCSS)
    fill(join(directory, 'views', 'index.html'), INDEX_HTML)
    fill(join(directory, 'views', 'layouts', 'base.html'), BASE_HTML)
    fill(join(directory, 'data.yml'), DATA_YML)

    touch(join(directory, 'javascripts', 'app.js'))


@cli.command()
@click.option('--target', type=click.Choice(['development', 'production']), 
    default='development', help='Build in development or production mode; default is `development`.')
def build(target):
    click.echo("Building...", nl=False)
    load_data()
    setup()
    stylesheets = css(target)
    js()
    images()
    render(stylesheets=stylesheets, target=target)
    click.echo(click.style("\tDone", fg='green'))


@cli.command()
def watch():
    click.echo("Watching...")

    observer.schedule(event_handler, path='javascripts/', recursive=True)
    observer.schedule(event_handler, path='stylesheets/', recursive=True)
    observer.schedule(event_handler, path='views/', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@cli.command()
def server():
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(("", PORT), Handler)

    print "serving at port", PORT
    os.chdir('dist/')
    httpd.serve_forever()