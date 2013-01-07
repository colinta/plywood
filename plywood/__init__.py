import string
import chomsky
from chomsky import (
    Literal, Char, Chars, StringEnd, NextIs, LineEnd,
    Optional,
    Buffer,
    # ParseException,
    )


class PlywoodNumber(chomsky.Number):
    pass


class PlywoodString(chomsky.String):
    pass


class PlywoodVariable(chomsky.Variable):
    pass


class PlywoodOperator(chomsky.Grammar):
    grammar = chomsky.Operator | chomsky.Assignment


class PlywoodParens(object):
    def __init__(self, values):
        self.values = values

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '(' + ', '.join(repr(v) for v in self.values) + ')'

    def __str__(self):
        return type(self).__name__ + '(' + ', '.join(repr(v) for v in self.values) + ')'


class PlywoodKvp(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '(' + repr(self.key) + ': ' + repr(self.value) + ')'

    def __str__(self):
        return repr(self.key) + ': ' + repr(self.value) + ')'


class PlywoodList(object):
    def __init__(self, values):
        self.values = values

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '[' + ', '.join(repr(v) for v in self.values) + ']'

    def __str__(self):
        return '[' + ', '.join(repr(v) for v in self.values) + ']'


class PlywoodDict(object):
    def __init__(self, values):
        self.values = values

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '{' + ', '.join(repr(v) for v in self.values) + '}'

    def __str__(self):
        return '{' + ', '.join(repr(v) for v in self.values) + '}'


tokens = [
    'open_block',
    'kvp',
    'dict_open',
    'dict_close',
]


class Plywood(object):
    VALUE_STATE = 1
    OPERATOR_STATE = 2

    testers = {
        'eof': StringEnd().test,
        'eol': (Literal('\n') | '\r\n' | '\r' | '#' | StringEnd).test,
        'comment': Literal('#').test,

        'variable': Char('_' + string.ascii_letters).test,
        'number': (Char('0123456789') | ('-' + Char('0123456789'))).test,
        'string': Char('"\'').test,

        'comma_close_parens': (Literal(',') | Literal(')')).test,
        'comma_close_list': (Literal(',') | Literal(']')).test,
        'colon_close_key': Literal(':').test,
        'comma_close_dict': (Literal(',') | Literal('}')).test,
    }

    matchers = {
        'comment': Literal('#') + NextIs(LineEnd()) | Char(),
        'number': PlywoodNumber,
        'string': PlywoodString,

        'operator': PlywoodOperator,

        ',': Char(','),
        ':': Char(':'),
        '=': Char('='),

        'parens_open': Literal('('),
        'parens_close': Literal(')'),
        'list_open': Literal('['),
        'list_close': Literal(']'),
        'dict_open': Literal('{'),
        'dict_close': Literal('}'),

        'single_whitespace': Chars(' \t'),
        'multiline_whitespace': Chars(' \t\r\n'),
    }

    matchers.update({
        'eol': Optional(matchers['comment']) + (Literal('\n') | '\r\n' | '\r' | StringEnd),
    })

    matchers.update({
        'blankline': Chars(' \t') + Optional(matchers['comment']) + matchers['eol'],
    })

    def __init__(self, input, parent=None):
        if not isinstance(input, Buffer):
            input = Buffer(input)
        self.buffer = input
        self.output = ''
        self.parent = parent

        self.scope = {
            'foo': 'bar',
            'bar': 'foo',
        }

    def run(self):
        parsed = self.parse()

    def parse(self):
        parsed = []
        while self.buffer:
            if self.test('blankline'):
                self.consume('blankline')
            else:
                self.whitespace = 'single_whitespace'
                line = self.consume_until('eol')
                parsed.append(line)
                self.consume('eol')
        return parsed

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def consume_until(self, until_token):
        line = []

        while not self.test(until_token):
            token = self.consume('value')
            line.append(token)

        self.figure_out_precedence(line, precedence=0)

        return line

    def figure_out_precedence(self, line, precedence):
        pass

    def consume_value(self):
        if self.test('variable'):
            retval = self.consume('variable')
        elif self.test('number'):
            retval = self.consume('number')
        elif self.test('string'):
            retval = self.consume('string')
        elif self.test('operator'):
            retval = self.consume('operator')
        elif self.test('parens_open'):
            retval = self.consume('parens')
        elif self.test('list_open'):
            retval = self.consume('list')
        elif self.test('dict_open'):
            retval = self.consume('dict')
        else:
            raise Exception(repr(self.buffer))
        self.consume('whitespace')

        return retval

    def consume_parens(self):
        self.consume('parens_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        retval = []
        while not self.test('parens_close'):
            self.consume('whitespace')
            item = self.consume_until('comma_close_parens')
            retval.append(item)
            if self.test(','):
                self.consume(',')
        self.consume('parens_close')
        self.whitespace = prev_whitespace

        return PlywoodParens(retval)

    def consume_list(self):
        self.consume('list_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        retval = []
        while not self.test('list_close'):
            self.consume('whitespace')
            item = self.consume_until('comma_close_list')
            retval.append(item)
            if self.test(','):
                self.consume(',')
        self.consume('list_close')
        self.whitespace = prev_whitespace

        return PlywoodList(retval)

    def consume_dict(self):
        self.consume('dict_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        retval = []
        while not self.test('dict_close'):
            self.consume('whitespace')
            key = self.consume_until('colon_close_key')
            self.consume(':')

            self.consume('whitespace')
            value = self.consume_until('comma_close_dict')

            retval.append(PlywoodKvp(key, value))
            if self.test(','):
                self.consume(',')
        self.consume('dict_close')
        self.whitespace = prev_whitespace

        return PlywoodDict(retval)

    def consume_variable(self):
        variable = PlywoodVariable(self.buffer)
        return variable

    def consume_whitespace(self):
        while self.buffer and self.test(self.whitespace):
            self.consume(self.whitespace)
            if self.whitespace == 'multiline_whitespace' and self.test('comment'):
                self.consume('comment')

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test(self, token, **kwargs):
        method = 'test_{0}'.format(token)
        if hasattr(self, method):
            return getattr(self, method)(**kwargs)
        try:
            return self.testers[token](self.buffer)
        except KeyError:
            return self.matchers[token].test(self.buffer)

    def consume(self, token, **kwargs):
        method = 'consume_{0}'.format(token)
        if hasattr(self, method):
            return getattr(self, method)(**kwargs)
        return self.matchers[token](self.buffer)
