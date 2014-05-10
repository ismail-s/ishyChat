"""Lexer for messages received by the chat client."""

import ply.lex as lex
import copy
from ishyChat.Utils.Constants import MENTION, HYPERLINK, NORMAL, WHITESPACE


tokens = (MENTION, HYPERLINK, NORMAL, WHITESPACE)
t_WHITESPACE = r'\s+'
####################
# These functions are in this order for a reason-it is the order
# in which they should be matched against. So don't start shifting
# them around without thinking carefully about it...
def t_MENTION(token):
    r'\@[^\s@]\S*'
    return token

def t_HYPERLINK(token):
    # This regex has already gone way out of control, and it is only meant
    # to do very loose identifying of hyperlinks...
    r'(?:https?://)?(?:www\.)?(?:[^\s\\/\.,]+)(?:\.[^\s,\.][^\s,]+)'
    return token

def t_NORMAL(token):
    r'\S+'
    return token
#####################

# Create the lexer
lexer = lex.lex()

def process(text):
    lexer.input(text)
    res = []
    for token in lexer:
        res.append((token.type, token.value))
    res = _simplify(res)
    return tuple(res)

def _simplify(tokens):
    """
    Takes a list of tokens as input and joins normal/whitespace tokens
    together.
    >>> _simplify([('HYPERLINK', 'example.com'),
    ... ('WHITESPACE', ' '),
    ... ('NORMAL', 'and'),
    ... ('WHITESPACE', ' '),
    ... ('NORMAL', 'text')])
    [('HYPERLINK', 'example.com'), ('NORMAL', ' and text')]
    """
    tokens = copy.deepcopy(tokens)

    res = []
    while True:
        next_res, number_of_combined_tokens = _get_next_simplified_token(tokens)
        if next_res:
            tokens = tokens[number_of_combined_tokens:]
            res.append(next_res)
        else:
            return res

def _get_next_simplified_token(tokens):
    """Helper function for _simplify function."""
    if not tokens:
        return (0, 0)
    if tokens[0][0] in (MENTION, HYPERLINK):
        return (tokens[0], 1)

    res = []
    for name, value in tokens:
        if name in (MENTION, HYPERLINK):
            combined_token = (NORMAL, ''.join([token[1] for token in res]))
            return (combined_token, len(res))
        res.append((name, value))
    combined_token = (NORMAL, ''.join([token[1] for token in res]))
    return (combined_token, len(res))

if __name__ == '__main__':
    test_cases = ['some text with @mention and example.com in it',
                '',
                'example.com, with some stuff @in it...\n as well '
                'http://me.net/testing this out',

                'finakl example with www.google.net, along with @yahoo '
                'and https:/bing.net']
    for e, test in enumerate(test_cases):
        print('Test case {}'.format(e + 1))
        print('=' * 10)
        res = process(test)
        print('final result: {}\n\n'.format(res))
