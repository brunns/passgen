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


class WordnikWordSource(object):
    def __init__(self, api_url=API_URL, api_key=API_KEY, max_api_calls=100, words_per_api_call=10):
        super(WordnikWordSource, self).__init__()

        client = swagger.ApiClient(api_key, api_url)
        self.words_api = WordsApi.WordsApi(client)
        self.words_per_api_call = words_per_api_call
        self.max_api_calls = max_api_calls

        # TODO Hard coded for now, as per https://en.wikipedia.org/wiki/Wordnik, but I'd like a better way
        self.length = 6925967

    def words(self):
        for _ in range(self.max_api_calls):
            words = self.words_api.getRandomWords(limit=self.words_per_api_call)
            logger.debug("words: %s", words)
            for word in words:
                logger.debug("word: %s", word)
                yield word.word


@app.route('/')
def generate():
    symbols = session.get('symbols', passgen.DEFAULT_SYMBOLS)
    patterns = session.get('patterns', "|".join(passgen.DEFAULT_PATTERNS))
    max_length = session.get('max_length', "%s" % passgen.DEFAULT_MAX_LENGTH)

    view = 'password.html'
    model = {'symbols': symbols, 'patterns': patterns, 'max_length': max_length,
             'symbols_help': passgen.SYMBOLS_HELP, 'patterns_help': passgen.PATTERNS_HELP,
             'maxlength_help': passgen.MAX_LENGTH_HELP}

    try:
        word_source = WordnikWordSource()
        password_generator = passgen.PasswordGenerator(word_source, symbol_set=symbols,
                                                       patterns=patterns.upper().split('|'), max_length=int(max_length))
        model['password'] = password_generator.next()
        model['entropy'] = password_generator.entropy
        model['error'] = False
    except passgen.PasswordsTooShort:
        model['password'] = passgen.PASSWORD_LENGTH_EXCEPTION_MESSAGE % max_length
        model['error'] = True
    except URLError as url_error:
        model['password'] = 'Failed to get random words from external service: "%s"' % url_error.reason
        model['error'] = True

    return render_template(view, **model)


@app.route('/set-options', methods=['POST'])
def set_options():
    session['symbols'] = request.form['symbols']
    session['patterns'] = request.form['patterns']
    session['max_length'] = request.form['max_length']

    return redirect(url_for('generate'))


@app.route('/reset-options', methods=['POST'])
def reset_options():
    del session['symbols']
    del session['patterns']
    del session['max_length']

    return redirect(url_for('generate'))


if __name__ == "__main__":
    app.run(debug=True)
