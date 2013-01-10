import string
import chomsky
from chomsky import (
    Literal, Char, Chars, StringEnd, LineEnd, Whitespace,
    Optional, ZeroOrMore,
    VariableGrammarType, OperatorGrammarType,
    Buffer,
    ParseException,
    )


class UnindentException(Exception):
    pass


class PlywoodNumberGrammar(chomsky.Number):
    def to_value(self):
        if isinstance(self.parsed, chomsky.Float):
            return PlywoodNumber(float(str(self)))

        base = 10
        if isinstance(self.parsed, chomsky.HexadecimalInteger):
            base = 16
        if isinstance(self.parsed, chomsky.OctalInteger):
            base = 8
        if isinstance(self.parsed, chomsky.BinaryInteger):
            base = 2
        return PlywoodNumber(int(str(self), base))


class PlywoodStringGrammar(chomsky.String):
    def to_value(self):
        parsed = self.parsed
        if isinstance(parsed, chomsky.TripleSingleQuotedString) or\
           isinstance(parsed, chomsky.TripleDoubleQuotedString):
            return PlywoodString(str(parsed), triple=True)
        return PlywoodString(str(parsed))


class PlywoodVariableGrammar(chomsky.Variable):
    __metaclass__ = VariableGrammarType
    starts_with = Char(string.ascii_letters + '_')
    ends_with = Chars(string.ascii_letters + '_' + string.digits, min=0)

    def to_value(self):
        return PlywoodVariable(str(self))


class PlywoodOperatorGrammar(chomsky.Grammar):
    __metaclass__ = OperatorGrammarType
    operators = [
        '==', '!=', '<=', '>=', '<', '>',
        'not', 'and', 'or', '&', '|', '~', '<<', '>>',
        '**',  '//',  '+',  '-',  '/',  '*',  '%',
        '.',  # getitem
        '@',  # id/name
        ',',  # auto arg
        '**=', '//=', '+=', '-=', '/=', '*=', '%=', '=',
    ]


class PlywoodValue(object):
    def to_value(self):
        return self


class PlywoodVariable(PlywoodValue):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, PlywoodVariable) and other.name == self.name

    def __repr__(self):
        return '{type.__name__}({self.name})'.format(type=type(self), self=self)

    __str__ = lambda self: self.name


class PlywoodString(PlywoodValue):
    def __init__(self, value, triple=False):
        self.triple = triple
        self.lang = None
        if triple:
            # unindent
            indent = None
            lines = value.splitlines()
            self.lang = lines.pop(0)
            lines.pop()

            for line in lines:
                if not line:
                    continue
                whitespace = str(Whitespace(' \t')(line))
                if indent is None or len(whitespace) < indent:
                    indent = whitespace
                    if not indent:
                        break
            if indent:
                lines = map(lambda line: line[len(indent):], lines)
                value = "\n".join(lines)
        self.value = value

    def __eq__(self, other):
        return self.value == str(other)

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        retval = self.value
        if self.triple:
            return '''"""{lang}\n{retval}\n"""'''.format(lang=self.lang, retval=retval)
        return repr(retval)


class PlywoodNumber(PlywoodValue):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        return str(self.value)


class PlywoodOperator(PlywoodValue):
    INDENT = ''

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        indent = type(self).INDENT
        type(self).INDENT += '  '
        retval = '{indent}{type.__name__}({self.left!r}\n{indent}  {self.operator!r}\n{indent}  {self.right!r}\n{indent})\n'.format(type=type(self), self=self, indent=indent)
        type(self).INDENT = indent
        return retval

    def __str__(self):
        op = str(self.operator)
        if self.operator not in ['.', '@']:
            op = ' ' + op + ' '
        return '{self.left}{op}{self.right}'.format(type=type(self), self=self, op=op)


class PlywoodFunction(PlywoodOperator):
    def __init__(self, left, right, block=None):
        super(PlywoodFunction, self).__init__('()', left, right)
        self.block = block

    def __repr__(self):
        indent = type(self).INDENT
        type(self).INDENT += '  '
        retval = '{indent}{type.__name__}({self.left!r} {self.right!r})'.format(type=type(self), self=self, indent=indent)
        if self.block:
            retval += ':\n'
            type(self).INDENT += '  '
            retval += repr(self.block)
        type(self).INDENT = indent
        return retval

    def __str__(self):
        indent = ''
        retval = '{indent}{self.left}{self.right}'.format(type=type(self), self=self, indent=indent)
        if self.block:
            retval += ':\n{indent}    {block}'.format(self=self, block=str(self.block).replace("\n", "\n    " + indent), indent=indent)
        return retval


class PlywoodUnaryOperator(PlywoodValue):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

    def __repr__(self):
        return '{type.__name__}({self.operator!r}, {self.value!r})'.format(type=type(self), self=self)


class PlywoodBlock(PlywoodValue):
    def __init__(self, lines):
        self.lines = lines

    def __getitem__(self, key):
        return self.lines.__getitem__(key)

    def __eq__(self, other):
        return self is other or \
            isinstance(other, list) and other == self.lines

    def __repr__(self):
        return type(self).__name__ + '(\n' + '\n'.join(repr(v) for v in self.lines) + '\n)'

    def __str__(self):
        return '\n'.join(str(v) for v in self.lines)


class PlywoodParens(PlywoodValue):
    def __init__(self, values, is_set=False):
        def convert_assign(value):
            if isinstance(value, PlywoodOperator) and value.operator == '=':
                # convert the 'variable' into a string
                if not isinstance(value.left, PlywoodVariable):
                    raise ParseException('Invalid keyword argument')
                key = PlywoodString(value.left.name)
                return PlywoodKvp(key, value.right, kwarg=True)
            return value

        values = map(convert_assign, values)
        is_kvp = lambda value: isinstance(value, PlywoodKvp)
        not_is_kvp = lambda value: not isinstance(value, PlywoodKvp)
        self.args = filter(not_is_kvp, values)
        self.kwargs = filter(is_kvp, values)
        self.is_set = is_set

    def __getitem__(self, key):
        return self.args.__getitem__(key)

    def __repr__(self):
        extra = ''
        if self.is_set and len(self.args) == 1:
            extra = ','
        return type(self).__name__ + '(' + ', '.join(repr(v) for v in self.args) + extra + ')'

    def __str__(self):
        extra = ''
        if self.is_set and len(self.args) == 1:
            extra = ','
        between = ''
        if self.args and self.kwargs:
            between = ', '
        return '(' + ', '.join(str(v) for v in self.args) + between + ', '.join(str(v) for v in self.kwargs) + extra + ')'


class PlywoodKvp(object):
    def __init__(self, key, value, kwarg=False):
        self.key = key
        self.value = value
        self.kwarg = kwarg

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    @property
    def separator(self):
        return self.kwarg and '=' or ': '

    def __repr__(self):
        return type(self).__name__ + '(' + repr(self.key) + self.separator + repr(self.value) + ')'

    def __str__(self):
        if self.separator == '=':
            return str(self.key)[1:-1] + self.separator + str(self.value)
        else:
            return str(self.key) + self.separator + str(self.value)


class PlywoodList(PlywoodValue):
    def __init__(self, values):
        self.values = values

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '[' + ', '.join(repr(v) for v in self.values) + ']'

    def __str__(self):
        return '[' + ', '.join(repr(v) for v in self.values) + ']'


class PlywoodDict(PlywoodValue):
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
    def __init__(self, input):
        if not isinstance(input, Buffer):
            input = Buffer(input)
        self.buffer = input
        self.output = ''
        self.block_indent = None
        self.prev_indent = []

        self.scope = {
            'foo': 'bar',
            'bar': 'foo',
        }

    def __repr__(self):
        return "{type.__name__}({self.buffer!r})".format(type=type(self), self=self)

    def run(self):
        return self.parse()

    def parse(self):
        return self.consume_block('')

    def consume_block(self, indent=None):
        """
        This is called when a ':' is found at the end of the line::
            if a: b
            if a:
                b

        and at the start of parsing, when the indent should be ''.

        If ``indent`` is None, we are at a ':'.  The colon is consumed, then
        single_whitespace, and then if we are at the end of the line, a block
        is consumed.  Otherwise we are at a token, and a single line is
        consumed.
        """
        self.prev_indent.append(self.block_indent)
        if indent is not None:
            self.block_indent = Literal(indent)
        else:
            self.block_indent = None
            self.consume('block_open')
            if self.test('blankspace'):
                self.consume('blankspace')

            # end of the line?
            if self.test('eol'):
                # yup, so continue - consume a multiline block
                self.consume('eol')
            else:
                # no!?  consume just the line, and nevermind about the prev_indent
                self.block_indent = self.prev_indent.pop()
                retval = PlywoodBlock([self.consume_until('eol', inline=True)])
                return retval

        parsed = []
        while self.buffer:
            if self.test('blankline'):
                self.consume('blankline')
            else:
                self.whitespace = 'single_whitespace'
                try:
                    line = self.consume_until('eol')
                except UnindentException:
                    while self.buffer[0] != '\n' and self.buffer[0] != '\r':
                        self.buffer.advance(-1)
                    break

                if line:
                    parsed.append(line)
                self.consume('eol')
        self.block_indent = self.prev_indent.pop()
        return PlywoodBlock(parsed)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    LTR = 1
    RTL = 2
    PRECEDENCE = {
        'high':  (100, LTR),
        '()':    (15, RTL),
        ':':     (15, RTL),
        'unary': (14, RTL),
        '.':     (13, LTR),
        '@':     (13, LTR),
        '**':    (12, RTL),
        '&':     (11, LTR),
        '|':     (10, LTR),
        '//':    (9, LTR),
        '/':     (9, LTR),
        '*':     (9, LTR),
        '+':     (8, LTR),
        '-':     (8, LTR),
        '%':     (7, LTR),
        '<<':    (6, LTR),
        '>>':    (6, LTR),
        '==':    (5, LTR),
        '!=':    (5, LTR),
        '<=':    (5, LTR),
        '>=':    (5, LTR),
        '<':     (5, LTR),
        '>':     (5, LTR),
        'and':   (4, LTR),
        'or':    (3, LTR),
        '**=':   (2, RTL),
        '//=':   (2, RTL),
        '+=':    (2, RTL),
        '-=':    (2, RTL),
        '/=':    (2, RTL),
        '*=':    (2, RTL),
        '%=':    (2, RTL),
        '=':     (2, RTL),
        ',':     (1, RTL),
        'low':   (0, RTL),
    }

    def operator_precedence(self, op):
        key = str(op)
        return self.PRECEDENCE[key]

    def consume_until(self, until_token, inline=False):
        # only eol consumers get the indent treatment
        if until_token == 'eol' and not inline:
            # the eol matcher should match the initial indent
            # if it's none, we need to figure out the indent
            # if it's too short, the block is done, and is rolled back to the
            # eol.  if it's too long, raise an exception.
            if not self.block_indent:
                whitespace = str(self.consume('optional_whitespace'))
                prev_indent = self.prev_indent[-1].literal
                if len(prev_indent) > len(whitespace):
                    raise ParseException('Expected: more indent')
                if len(prev_indent) == len(whitespace):
                    raise UnindentException()

                self.block_indent = Literal(whitespace)
            else:
                if not self.block_indent.test(self.buffer):
                    raise UnindentException()

                indent = self.block_indent.consume(self.buffer)
                if self.test('single_whitespace'):
                    extra = self.consume('single_whitespace')
                    raise ParseException('Unexpected: too much indent. '
                        'found {extra!r} ({len_extra}) '
                        'instead of {indent!r} ({len_indent})'.format(extra=indent + extra, len_extra=len(indent) + len(extra),
                                                        indent=indent, len_indent=len(indent)))

        line = []
        while not self.test(until_token):
            token = self.consume_token()
            line.append(token)

        if line:
            return self.figure_out_precedence(line)[0]
        return None

    DEFAULT_PRECEDENCE = (-1, LTR)

    def figure_out_precedence(self, line, index=0, precedence=DEFAULT_PRECEDENCE):
        """
        This method is a process of reducing a list of tokens into one value. It
        is responsible for most of the language grammar, like operator
        precendence, where special syntaxes like keyword arguments are allowed,
        and consuming blocks.

        It works basically by scanning the items in line until the precedence is
        less than the current precedence.  ``left`` holds the current value,
        and is either 'merged' into the right value via an operation, or it is
        returned so that scanning can continue at a lower precedence.
        """
        if len(line) == index:
            raise ParseException('Expected: value')
        precedence_order, direction = precedence
        new_precedence = None
        left = line[index]
        index += 1
        if len(line) == index:
            return left.to_value(), index

        while index < len(line):
            if isinstance(left, PlywoodOperatorGrammar):
                right, index = self.figure_out_precedence(line, index, self.PRECEDENCE['unary'])
                left = PlywoodUnaryOperator(operator=str(left), value=right)
            else:
                left = left.to_value()
                op = line[index]
                index += 1

                if isinstance(op, PlywoodParens):
                    left = PlywoodFunction(left, op)
                elif isinstance(op, PlywoodBlock):
                    # precedence checking for the block - it can only be bound
                    # at the lowest precedence
                    if precedence_order >= self.operator_precedence('low')[0]:
                        return left, index - 1

                    if isinstance(left, PlywoodFunction):
                        left.block = op
                    else:
                        left = PlywoodFunction(left, PlywoodParens([]), op)
                elif not isinstance(op, PlywoodOperatorGrammar):
                    # this is the 'auto call' section - when two non-operators
                    # are next to each other, the right token is passed to the
                    # left.  It has the lowest precedence.
                    index -= 1
                    right, index = self.figure_out_precedence(line, index, self.operator_precedence('low'))
                    # right could be a series of 'token,token' operations.  flatten those out
                    right = self.convert_to_args(right)
                    left = PlywoodFunction(left, right)
                elif isinstance(op, PlywoodOperatorGrammar):
                    new_precedence = self.operator_precedence(op)
                    new_order, new_direction = new_precedence

                    if new_order < precedence_order or (new_order == precedence_order and direction == self.LTR):
                        return left, index - 1
                    elif new_order > precedence_order or (new_order == precedence_order and direction == self.RTL):
                        right, index = self.figure_out_precedence(line, index, new_precedence)
                    left = PlywoodOperator(str(op), left, right)
                else:
                    raise Exception('Unknown token "{op!r}"'.format(op=op))
        return left, index

    def convert_to_args(self, token):
        tokens = []
        while isinstance(token, PlywoodOperator) and token.operator == ',':
            tokens.append(token.left)
            token = token.right
        tokens.append(token)

        return PlywoodParens(tokens)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    TOKEN_TESTS = (
        ('number', 'number'),
        ('operator', 'operator'),
        ('variable', 'variable'),
        ('string', 'string'),
        ('parens_open', 'parens'),
        ('list_open', 'list'),
        ('dict_open', 'dict'),
        ('block_open', 'block'),
    )

    def consume_token(self):
        retval = None
        for token_test, token_consume in self.TOKEN_TESTS:
            if self.test(token_test):
                retval = self.consume(token_consume)
                break

        if not retval:
            raise Exception(repr(self.buffer))
        self.consume('whitespace')

        return retval

    def consume_variable(self):
        variable = PlywoodVariableGrammar(self.buffer)
        return variable

    def consume_whitespace(self):
        while self.buffer and self.test(self.whitespace):
            self.consume(self.whitespace)
            if self.whitespace == 'multiline_whitespace' and self.test('comment'):
                self.consume('comment')

    def consume_parens(self):
        self.consume('parens_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        tokens = []
        is_set = False
        while not self.test('parens_close'):
            self.consume('whitespace')
            item = self.consume_until('comma_close_parens')
            if item:
                tokens.append(item)
            if self.test(','):
                is_set = True
                self.consume(',')
        self.consume('parens_close')
        self.whitespace = prev_whitespace

        return PlywoodParens(tokens, is_set=is_set)

    def consume_list(self):
        self.consume('list_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        tokens = []
        while not self.test('list_close'):
            self.consume('whitespace')
            item = self.consume_until('comma_close_list')
            tokens.append(item)
            if self.test(','):
                self.consume(',')
        self.consume('list_close')
        self.whitespace = prev_whitespace

        return PlywoodList(tokens)

    def consume_dict(self):
        self.consume('dict_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        tokens = []
        while not self.test('dict_close'):
            self.consume('whitespace')
            key = self.consume_until('colon_close_key')
            self.consume(':')

            self.consume('whitespace')
            value = self.consume_until('comma_close_dict')

            tokens.append(PlywoodKvp(key, value))
            if self.test(','):
                self.consume(',')
        self.consume('dict_close')
        self.whitespace = prev_whitespace

        return PlywoodDict(tokens)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    TESTERS = {
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

    MATCHERS = {
        'comment': Literal('#') + ZeroOrMore(Char('\r\n', inverse=True)) + LineEnd(),
        'number': PlywoodNumberGrammar,
        'string': PlywoodStringGrammar,

        'operator': PlywoodOperatorGrammar,

        ',': Char(','),
        ':': Char(':'),
        '=': Char('='),

        'parens_open': Literal('('),
        'parens_close': Literal(')'),
        'list_open': Literal('['),
        'list_close': Literal(']'),
        'dict_open': Literal('{'),
        'dict_close': Literal('}'),
        'block_open': Literal(':'),

        'single_whitespace': Chars(' \t'),
        'multiline_whitespace': Chars(' \t\r\n'),
        'optional_whitespace': Whitespace(' \t'),
    }

    MATCHERS.update({
        'eol': Optional(MATCHERS['comment']) + (Literal('\n') | '\r\n' | '\r' | StringEnd),
    })

    MATCHERS.update({
        'blankspace': Optional(MATCHERS['single_whitespace']) + Optional(MATCHERS['comment']),
    })

    MATCHERS.update({
        'blankline': MATCHERS['blankspace'] + MATCHERS['eol'],
    })

    def test(self, token, **kwargs):
        method = 'test_{0}'.format(token)
        if hasattr(self, method):
            return getattr(self, method)(**kwargs)
        try:
            return self.TESTERS[token](self.buffer)
        except KeyError:
            return self.MATCHERS[token].test(self.buffer)

    def consume(self, token, **kwargs):
        method = 'consume_{0}'.format(token)
        if hasattr(self, method):
            return getattr(self, method)(**kwargs)
        return self.MATCHERS[token](self.buffer)
