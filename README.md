# kulfon

Kulfon is a simple and fast static site generator written in Python. By default is uses [jinja2][1] for templating, [libsass][2] for stylesheets compilation and [webpack][3] for bundling javascript files. External assets are managed using [Bower][4].

Goals:

* fast
* easy to install
* no `npm` nor `node_modules` directory which is large and takes time to install
* by default a templating language easy to understand by designers
* no need to write extra wrappers for existing tools 
* ES6/7 ready
* use [Bower][4] because of flat dependency structure

## Install

    pip install kulfon


## Usage

### `init`

    kulfon init [directory]

It creates the following directory structure (`directory` is optional, if not provided, the current directory is used):

```
.
├── data.yml
├── images
├── javascripts
├── stylesheets
└── views
    ├── index.html
    ├── layouts
    │   └── base.html
    └── partials
```

* `data.yml` 

### `build`

    kulfon build

It builds the project, which consists of:
- creating `dist/` directory
- creating `styles.css` file inside `dist/assets` using `libsass` compiler
- creating `vendor.js` file insdie `dist/assets` 
- creating `app.js` file insdie `dist/assets` 
- moving images from `images` to `dist/assets`

[1]: http://jinja.pocoo.org/docs/dev/
[2]: http://sass-lang.com/libsass
[4]: http://bower.io/