#!/usr/bin/env python
# encoding: utf-8
"""
Generate password.
"""
import optparse
import os
import sys
import warnings
import random
import logging
import itertools

__author__ = 'Simon Brunning'
__version__ = "0.11"

script_name = os.path.basename(sys.argv[0])
usage = script_name + ' [options] args'
description = '''
Generate password.
'''

logger = logging.getLogger(script_name)

CASE_FUNCTIONS = (lambda x: x.lower(), lambda x: x.upper(), lambda x: x.capitalize())
DEFAULT_PATTERN = "WSW2|W2WS|WS2W|W2SW|WSW2W|W2WSW"
DEFAULT_WORDFILE = "/usr/share/dict/words"
DEFAULT_SYMBOLS = "-=[];\"'\\,./!@$%^*()_:<>?"
DEFAULT_MAX_LENGTH = 128
DEFAULT_WORD_LENGTH = 12


def main(*argv):
    options, script, args, help = get_options(argv)
    init_logger(options.verbosity)
    logger.debug(options)

    patterns = options.pattern.upper().split('|')
    try:
        generated_password = generate_password(word_source(options.wordfile), options.symbols, patterns, options.max_length,
                                               options.max_word_length)
        print generated_password
    except PasswordsTooShort, passwords_too_short:
        print "Unable to generate password with length %s. " \
              "Try a shorter pattern, or a longer password length." % passwords_too_short.max_length


def word_source(wordfile):
    with open(wordfile) as words:
        for word in words:
            yield word


def generate_password(word_source, symbol_set=DEFAULT_SYMBOLS,
                      patterns=DEFAULT_PATTERN.upper().split('|'), max_length=DEFAULT_MAX_LENGTH,
                      max_word_length=DEFAULT_WORD_LENGTH):
    words = (word.strip()
             for word
             in random_items(word_source, 999)
             if len(word.strip()) < max_word_length and not word.strip().endswith("'s"))

    random_cased_words = (random.choice(CASE_FUNCTIONS)(word) for word in words)
    upper = (word.upper() for word in words)
    lower = (word.lower() for word in words)
    capitalised = (word.capitalize() for word in words)

    symbols = repeatfunc(lambda: "".join(random.sample(symbol_set, random.randint(1, 3))))
    spaces = itertools.repeat(" ")

    password_element_iterators = {"W": random_cased_words,
                                  "U": upper,
                                  "L": lower,
                                  "C": capitalised,
                                  "S": symbols,
                                  " ": spaces}
    for length in range(1, 10):
        password_element_iterators['%s' % length] = generate_number(length)

    pattern = random.choice(patterns)
    logger.debug("pattern, %s", pattern)

    while 1:
        try:
            candidate = "".join([password_element_iterators[pattern_element].next() for pattern_element in pattern])
        except StopIteration:
            raise PasswordsTooShort(max_length)

        logger.debug("candidate, %s", candidate)
        if len(candidate) <= max_length:
            return candidate


def random_items(iterable, items_wanted=1):
    """Pick random items with equal probability from an iterable, iterating only once.

    http://code.activestate.com/recipes/426332/
    """
    result = [None] * items_wanted
    for index, item in enumerate(iterable):
        if index < items_wanted:
            result[index] = item
        else:
            target = int(random.random() * (index + 1))
            if target < items_wanted:
                result[target] = item
    random.shuffle(result)
    return result


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)

    http://docs.python.org/2/library/itertools.html#recipes
    """
    if times is None:
        return itertools.starmap(func, itertools.repeat(args))
    return itertools.starmap(func, itertools.repeat(args, times))


def generate_number(length):
    return repeatfunc(lambda: ("%%0%sd" % length) % random.randint(0, 10 ** length - 1))


class PasswordsTooShort(Exception):
    def __init__(self, max_length, *args, **kwargs):
        super(PasswordsTooShort, self).__init__(*args, **kwargs)
        self.max_length = max_length


def get_options(argv):
    """Get options and arguments from argv string."""
    parser = optparse.OptionParser(usage=usage, version=__version__)
    parser.description = description
    parser.add_option("-v", "--verbosity", action="count", default=0,
                      help="Specify up to three times to increase verbosity, i.e. -v to see warnings, -vv for "
                           "information messages, or -vvv for debug messages.")

    parser.add_option("-p", "--pattern", action="store", default=DEFAULT_PATTERN,
                      help="Password pattern. "
                           "W=word, "
                           "U=upper-cased word, "
                           "L=lower-cased word, "
                           "C=capitalised word, "
                           "S=symbols, "
                           "n=number with n (1-9) digits, "
                           "' '=space. "
                           "Multiple patterns may be provided, separated by '|' characters. "
                           "One pattern will be selected at random.  Defaults to %default. "
                           "http://xkcd.com/936/ style passwords can be generated with 'l l l l'.")
    parser.add_option("-w", "--wordfile", action="store", default=DEFAULT_WORDFILE,
                      help="Text file containing list of words. Defaults to %default.")
    parser.add_option("-s", "--symbols", action="store", default=DEFAULT_SYMBOLS,
                      help="List of symbols to pick from to include in password. Defaults to %default.")
    parser.add_option("-l", "--max-length", action="store", type="int", default=DEFAULT_MAX_LENGTH,
                      help="Maximum length for generated password. Defaults to %default.")
    parser.add_option("--max-word-length", action="store", type="int", default=DEFAULT_WORD_LENGTH,
                      help="Maximum length for word elements. Defaults to %default.")

    options, args = parser.parse_args(list(argv))
    script, args = args[0], args[1:]
    return options, script, args, parser.format_help()


def init_logger(verbosity, stream=sys.stdout):
    """Initialize logger and warnings according to verbosity argument.
    Verbosity levels of 0-3 supported."""
    is_not_debug = verbosity <= 2
    level = [logging.ERROR, logging.WARNING, logging.INFO][verbosity] if is_not_debug else logging.DEBUG
    log_format = '%(message)s' if is_not_debug \
        else '%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s'
    logging.basicConfig(level=level, format=log_format, stream=stream)
    if is_not_debug: warnings.filterwarnings('ignore')


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
