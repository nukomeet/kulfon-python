from setuptools import setup

setup(
    name='kulfon',
    description='Fast and simple static site generator',
    author='Zaiste',
    author_email='oh@zaiste.net',
    version='0.2.0',
    py_modules=['kulfon'],
    install_requires=[
        'click',
        'libsass',
        'pyyaml',
        'jinja2',
        'watchdog'
    ],
    entry_points='''
        [console_scripts]
        kulfon=kulfon:cli
    ''',
)