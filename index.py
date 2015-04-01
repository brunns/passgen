#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
import passgen

app = Flask(__name__)
app.debug = True


@app.route('/')
def password():
    return passgen.generate_password()
