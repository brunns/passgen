# passgen

Simple Flask on heroku app to generate strong passwords.

## Prerequisites

You'll need the following installed:

* [Python 2.x](https://www.python.org/)
* [Heroku Toolbelt](https://toolbelt.heroku.com/)
* [Virtualenv](https://virtualenv.pypa.io/)

If these commands give you a version number, you are good to go:

    $ virtualenv --version
    $ heroku --version

You'll also need a developer key from [Worknik](http://developer.wordnik.com/).

## Doing stuff

[Getting Started with Python on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python-o) is a pretty good starting point.

### Creating and activating virtualenv

    $ virtualenv venv --no-site-packages # Only once
    $ source venv/bin/activate # Every time

### Installing dependencies in virtualenv

    $ pip install -r requirements.txt

### Local configuration

You'll need to create a `.env` file containing:

    WORDNIK_API_KEY=[Your Worknik key here]
    DEBUG=True
    COOKIE_SECRET_KEY=[Big random string]

### Running the app

    $ foreman start

### Updating dependencies

    $ pip freeze > requirements.txt
