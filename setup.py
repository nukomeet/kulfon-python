from setuptools import setup

setup(
    name='kulfon',
    description='Fast and simple static site generator',
    author='Zaiste',
    author_email='oh@zaiste.net',
    version='0.2.11',
    py_modules=['kulfon'],
    install_requires=[
        'click',
        'pyyaml',
        'jinja2',
        'livereload',
        'libsass',
        'colorama',
        'webassets'
    ],
    entry_points='''
        [console_scripts]
        kulfon=kulfon:cli
    ''',
)
