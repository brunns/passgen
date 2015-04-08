#!/usr/bin/env python
# encoding: utf-8
'''
Simple Flask app for generating passwords
'''

from flask import Flask
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
        word = words_api.getRandomWord().word
        logger.debug("word: %s", word)
        yield word

@app.route('/')
def password():
    return passgen.generate_password(word_source=word_source())

if __name__ == "__main__":
    app.run(debug=True)
