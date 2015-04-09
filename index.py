#!/usr/bin/env python
# encoding: utf-8
'''
Simple Flask app for generating passwords
'''

from flask import Flask, render_template, request
from wordnik import swagger, WordsApi
import logging
import os
import passgen

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = bool(os.environ['DEBUG'])


def word_source():
    api_url = 'http://api.wordnik.com/v4'
    api_key = os.environ['WORDNIK_API_KEY']
    client = swagger.ApiClient(api_key, api_url)
    words_api = WordsApi.WordsApi(client)
    while True:
        word = words_api.getRandomWord().word  # URLError potential here
        logger.debug("word: %s", word)
        yield word

@app.route('/')
def password():
    symbols = request.args['symbols'] if 'symbols' in request.args else passgen.DEFAULT_SYMBOLS
    pattern = request.args['pattern'] if 'pattern' in request.args else passgen.DEFAULT_PATTERN
    max_length = int(request.args['max_length']) if 'max_length' in request.args else passgen.DEFAULT_MAX_LENGTH

    generated_password = passgen.generate_password(word_source=word_source(), symbol_set=symbols, patterns=pattern.upper().split('|'), max_length=max_length)
    return render_template('password.html', password=generated_password, symbols=symbols, pattern=pattern, max_length=max_length)

if __name__ == "__main__":
    app.run(debug=True)
