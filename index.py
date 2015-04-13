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


class WordnikPasswordGenerator(passgen.AbstractPasswordGenerator):
    def __init__(self, symbol_set=passgen.DEFAULT_SYMBOLS, patterns=passgen.DEFAULT_PATTERNS,
                 max_length=passgen.DEFAULT_MAX_LENGTH, max_word_length=passgen.DEFAULT_WORD_LENGTH):
        super(WordnikPasswordGenerator, self).__init__(symbol_set, patterns, max_length, max_word_length)
        api_url = 'http://api.wordnik.com/v4'
        api_key = os.environ['WORDNIK_API_KEY']
        client = swagger.ApiClient(api_key, api_url)
        self.words_api = WordsApi.WordsApi(client)

    def word_source(self, words_per_api_call=10, max_api_calls=100):
        for _ in range(max_api_calls):
            words = self.words_api.getRandomWords(limit=words_per_api_call)  # TODO: Potential URLError here if API unavailable
            logger.debug("words: %s", words)
            for word in words:
                logger.debug("word: %s", word)
                yield word.word


@app.route('/')
def password():
    symbols = request.args['symbols'] if 'symbols' in request.args else passgen.DEFAULT_SYMBOLS
    patterns = request.args['pattern'].upper().split('|') if 'pattern' in request.args else passgen.DEFAULT_PATTERNS
    max_length = int(request.args['max_length']) if 'max_length' in request.args else passgen.DEFAULT_MAX_LENGTH

    try:
        password_generator = WordnikPasswordGenerator(symbol_set=symbols, patterns=patterns, max_length=max_length)
        generated_password = password_generator.next()
        error = False
    except passgen.PasswordsTooShort:
        generated_password = passgen.PASSWORD_LENGTH_EXCEPTION_MESSAGE % max_length
        error = True
    return render_template('password.html', password=generated_password, symbols=symbols, patterns="|".join(patterns),
                           max_length=max_length, symbols_help=passgen.SYMBOLS_HELP,
                           patterns_help=passgen.PATTERNS_HELP, maxlength_help=passgen.MAX_LENGTH_HELP, error=error)


if __name__ == "__main__":
    app.run(debug=True)
