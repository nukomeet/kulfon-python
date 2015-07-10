# kulfon 

A static site generator that uses [stasis][1] for the content and 
[broccoli][2] for the assets.

## Features

## Install
  
    git clone git@github.com:nukomeet/kulfon.git website

    gem install stasis

    cd website 
    bower install

    npm install


## Usage

    cd website 
    npm start

## Build

    cd website 
    npm run build

    cd dist
    python -m SimpleHTTPServer 8081

Open `localhost:8081`


[1]: http://stasis.me/ 
[2]: https://github.com/broccolijs/broccoli