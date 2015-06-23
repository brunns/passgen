#!/usr/bin/env python
# encoding: utf-8
"""
Simple Flask app for generating passwords
"""
from urllib2 import URLError
from flask import Flask, redirect, render_template, request, session, url_for
from wordnik import swagger, WordsApi
import logging
import os
import passgen


logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = bool(os.environ['DEBUG'])

app.secret_key = os.environ['COOKIE_SECRET_KEY']

API_KEY = os.environ['WORDNIK_API_KEY']
API_URL = 'http://api.wordnik.com/v4'


class WordnikPasswordGenerator(passgen.AbstractPasswordGenerator):
    def __init__(self, symbol_set=passgen.DEFAULT_SYMBOLS, patterns=passgen.DEFAULT_PATTERNS,
                 max_length=passgen.DEFAULT_MAX_LENGTH, max_word_length=passgen.DEFAULT_WORD_LENGTH):
        super(WordnikPasswordGenerator, self).__init__(symbol_set, patterns, max_length, max_word_length)

        client = swagger.ApiClient(API_KEY, API_URL)
        self.words_api = WordsApi.WordsApi(client)

    def word_source(self, words_per_api_call=10, max_api_calls=100):
        for _ in range(max_api_calls):
            words = self.words_api.getRandomWords(limit=words_per_api_call)
            logger.debug("words: %s", words)
            for word in words:
                logger.debug("word: %s", word)
                yield word.word


@app.route('/')
def password():
    symbols = session.get('symbols', passgen.DEFAULT_SYMBOLS)
    patterns = session.get('patterns', "|".join(passgen.DEFAULT_PATTERNS))
    max_length = session.get('max_length', "%s" % passgen.DEFAULT_MAX_LENGTH)

    view = 'password.html'
    model = {'symbols': symbols, 'patterns': patterns, 'max_length': max_length,
             'symbols_help': passgen.SYMBOLS_HELP, 'patterns_help': passgen.PATTERNS_HELP,
             'maxlength_help': passgen.MAX_LENGTH_HELP}

    try:
        password_generator = WordnikPasswordGenerator(symbol_set=symbols,
                                                      patterns=patterns.upper().split('|'),
                                                      max_length=int(max_length))
        model['password'] = password_generator.next()
        model['error'] = False
    except passgen.PasswordsTooShort:
        model['password'] = passgen.PASSWORD_LENGTH_EXCEPTION_MESSAGE % max_length
        model['error'] = True
    except URLError as url_error:
        model['password'] = 'Failed to get random words from external service: "%s"' % url_error.reason
        model['error'] = True

    return render_template(view, **model)


@app.route('/generate', methods=['POST'])
def generate():
    session['symbols'] = request.form['symbols']
    session['patterns'] = request.form['patterns']
    session['max_length'] = request.form['max_length']

    return redirect(url_for('password'))


@app.route('/reset', methods=['POST'])
def reset():
    del session['symbols']
    del session['patterns']
    del session['max_length']

    return redirect(url_for('password'))


if __name__ == "__main__":
    app.run(debug=True)
