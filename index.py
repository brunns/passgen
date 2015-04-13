#!/usr/bin/env python
# encoding: utf-8
"""
Simple Flask app for generating passwords
"""

from flask import Flask, render_template, request
from wordnik import swagger, WordsApi
import logging
import os
import passgen

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = bool(os.environ['DEBUG'])


def word_source(words_per_api_call=10, max_api_calls=100):
    api_url = 'http://api.wordnik.com/v4'
    api_key = os.environ['WORDNIK_API_KEY']
    client = swagger.ApiClient(api_key, api_url)
    words_api = WordsApi.WordsApi(client)
    for _ in range(max_api_calls):
        words = words_api.getRandomWords(limit=words_per_api_call)
        logger.debug("words: %s", words)
        for word in words:
            logger.debug("word: %s", word)
            yield word.word


@app.route('/')
def password():
    symbols = request.args['symbols'] if 'symbols' in request.args else passgen.DEFAULT_SYMBOLS
    pattern = request.args['pattern'] if 'pattern' in request.args else passgen.DEFAULT_PATTERN
    max_length = int(request.args['max_length']) if 'max_length' in request.args else passgen.DEFAULT_MAX_LENGTH

    generated_password = passgen.generate_password(word_source=word_source(), symbol_set=symbols,
                                                   patterns=pattern.upper().split('|'),
                                                   max_length=max_length)  # TODO: PasswordsTooShort potential here
    return render_template('password.html', password=generated_password, symbols=symbols, pattern=pattern,
                           max_length=max_length, symbols_help=passgen.SYMBOLS_HELP, pattern_help=passgen.PATTERN_HELP,
                           maxlength_help=passgen.MAX_LENGTH_HELP)


if __name__ == "__main__":
    app.run(debug=True)
