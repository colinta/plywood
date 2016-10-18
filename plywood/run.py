import string
from chomsky import (
    Literal, Char, Chars, StringEnd, LineEnd, Whitespace,
    Optional, ZeroOrMore,
    Buffer,
    ParseException,
    )
from grammar import (
    PlywoodNumberGrammar,
    PlywoodStringGrammar,
    PlywoodVariableGrammar,
    PlywoodOperatorGrammar,
    )
from values import (
    PlywoodValue,
    PlywoodOperator,
    PlywoodCallOperator,
    PlywoodUnaryOperator,
    PlywoodBlock,
    PlywoodParens,
    PlywoodKvp,
    PlywoodList,
    PlywoodXml,
    PlywoodSlice,
    PlywoodIndices,
    PlywoodDict,
    )
from plywood.env import PlywoodEnv
from exceptions import UnindentException, BreakException
from scope import Scope


def plywood(input, context={}, **options):
    runtime = PlywoodEnv(options)
    return Plywood(input).run(context, runtime)


class Plywood(object):
    def __init__(self, input):
        if isinstance(input, unicode):
            self.input = input
        else:
            self.input = unicode(input, 'utf-8')
        self.buffer = Buffer(self.input)
        self.output = ''
        self.block_indent = None
        self.prev_indent = []
        self.parsed = None

    def __repr__(self):
        return "{type.__name__}({self.buffer!r})".format(type=type(self), self=self)

    def run(self, context, runtime):
        parsed = self.compile()
        runtime.scope['__input'] = self.input
        runtime.scope['self'] = Scope(context)
        try:
            retval = parsed.python_value(runtime.scope)
        except BreakException as e:
            retval = e.retval
        return retval

    def compile(self):
        if self.parsed is None:
            self.parsed = self.consume_block('')
        return self.parsed

    def consume_block(self, indent=None):
        """
        This is called when a ':' is found at the end of the line::
            if a: b
            if a:
                b

        and at the start of parsing, when the indent should be ''.

        If ``indent`` is None, we are at a ':'.  The colon is consumed, then
        singleline_whitespace, and then if we are at the end of the line, a
        block is consumed.  Otherwise we are at a token, and a single line is
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
                location = self.buffer.position
                return PlywoodBlock(location, [self.consume_until('eol', inline=True)], inline=True)

        parsed = []
        location = self.buffer.position
        while self.buffer:
            if self.test('blankline'):
                self.consume('blankline')
            else:
                self.whitespace = 'singleline_whitespace'
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
        return PlywoodBlock(location, parsed, inline=len(parsed) == 0)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    LTR = 1
    RTL = 2
    PRECEDENCE = {
        'high':  (100, LTR),
        # '|':     (18, LTR),
        '[]':    (17, LTR),
        '.':     (17, LTR),
        '@':     (17, LTR),
        '()':    (16, LTR),
        '**':    (14, RTL),
        'unary': (13, RTL),
        '|':     (11, LTR),
        '//':    (10, LTR),
        '/':     (10, LTR),
        '*':     (10, LTR),
        '+':     (9, LTR),
        '-':     (9, LTR),
        '%':     (8, LTR),
        '==':    (5, LTR),
        '!=':    (5, LTR),
        '<=':    (5, LTR),
        '>=':    (5, LTR),
        '<':     (5, LTR),
        '>':     (5, LTR),
        'in':    (5, RTL),
        'is':    (5, RTL),
        'and':   (4, LTR),
        'or':    (3, LTR),
        '**=':   (2, RTL),
        '//=':   (2, RTL),
        '+=':    (2, RTL),
        '-=':    (2, RTL),
        '/=':    (2, RTL),
        '*=':    (2, RTL),
        '%=':    (2, RTL),
        '|=':    (2, RTL),
        'or=':   (2, RTL),
        '&=':    (2, RTL),
        'and=':  (2, RTL),
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
                    raise UnindentException()
                    raise ParseException('Expected: more indent at {self.buffer!r}'.format(self=self))
                if len(prev_indent) == len(whitespace):
                    raise UnindentException()

                self.block_indent = Literal(whitespace)
            else:
                if not self.block_indent.test(self.buffer):
                    raise UnindentException()

                indent = self.block_indent.consume(self.buffer)
                if self.test('singleline_whitespace'):
                    extra = self.consume('singleline_whitespace')
                    raise ParseException('Unexpected: too much indent. '
                        'found {extra!r} ({len_extra}) '
                        'instead of {indent!r} ({len_indent})'.format(extra=indent + extra, len_extra=len(indent) + len(extra),
                                                        indent=indent, len_indent=len(indent)))

        line = []
        prev = None
        while not self.test(until_token):
            prev_is_operator = not prev or isinstance(prev, PlywoodOperatorGrammar)
            token = self.consume_token(prev_is_operator=prev_is_operator)
            prev = token
            # there is an unfortunate exception for '['.  As an operator, it is
            # the 'get_item' operator, but as a token it is a list token.  this
            # must be resolved *before* figure_out_precedence is called.
            is_indexable = isinstance(token, PlywoodList) or isinstance(token, PlywoodSlice)
            if is_indexable and not prev_is_operator:
                op = PlywoodOperatorGrammar('[]')
                op.location = token.location
                line.append(op)
                if isinstance(token, PlywoodList):
                    token = PlywoodIndices(token.location, token.values, token.force_list)
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
            return left.plywood_value(), index

        while index < len(line):
            if isinstance(left, PlywoodOperatorGrammar):
                right, index = self.figure_out_precedence(line, index, self.PRECEDENCE['unary'])
                left = PlywoodUnaryOperator(left.location, operator=str(left), value=right)
            else:
                left = left.plywood_value()
                op = line[index]
                index += 1

                if isinstance(op, PlywoodParens):
                    if precedence_order >= self.operator_precedence('()')[0]:
                        return left, index - 1
                    left = PlywoodCallOperator(left, op)
                elif isinstance(op, PlywoodBlock):
                    # precedence checking for the block - it can only be bound
                    # at the lowest precedence
                    if precedence_order >= self.operator_precedence('low')[0]:
                        return left, index - 1

                    if isinstance(left, PlywoodCallOperator):
                        left.block = op
                    else:
                        left = PlywoodCallOperator(left, PlywoodParens(left.location, []), op)
                elif isinstance(op, PlywoodOperatorGrammar):
                    new_precedence = self.operator_precedence(op)
                    new_order, new_direction = new_precedence

                    if new_order < precedence_order or (new_order == precedence_order and direction == self.LTR):
                        return left, index - 1
                    elif new_order > precedence_order or (new_order == precedence_order and direction == self.RTL):
                        right, index = self.figure_out_precedence(line, index, new_precedence)
                    left = PlywoodOperator(str(op), left, right)
                else:
                    # this is the 'auto call' section - when two non-operators
                    # are next to each other, the right token is passed to the
                    # left.  It has the lowest precedence.
                    index -= 1
                    right, index = self.figure_out_precedence(line, index, self.operator_precedence('low'))
                    # right could be a series of 'token,token' operations.  flatten those out
                    right = self.convert_to_args(left.location, right)
                    left = PlywoodCallOperator(left, right)
        return left, index

    def convert_to_args(self, location, token):
        tokens = []
        while isinstance(token, PlywoodOperator) and token.operator == ',':
            tokens.append(token.left)
            token = token.right
        tokens.append(token)

        return PlywoodParens(location, tokens)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    TOKEN_TESTS_VAL = (
        ('from', 'from'),
        ('number', 'number'),
        ('xml_open', 'xml'),
        ('operator', 'operator'),
        ('variable', 'variable'),
        ('string', 'string'),
        ('parens_open', 'parens'),
        ('list_open', 'list'),
        ('dict_open', 'dict'),
        ('block_open', 'block'),
    )
    TOKEN_TESTS_OP = (
        ('from', 'from'),
        ('number', 'number'),
        ('operator', 'operator'),
        ('variable', 'variable'),
        ('string', 'string'),
        ('parens_open', 'parens'),
        ('xml_open', 'xml'),
        ('list_open', 'list'),
        ('dict_open', 'dict'),
        ('block_open', 'block'),
    )

    def consume_token(self, prev_is_operator=False):
        retval = None
        TOKEN_TESTS = prev_is_operator and self.TOKEN_TESTS_VAL or self.TOKEN_TESTS_OP
        for token_test, token_consume in TOKEN_TESTS:
            if self.test(token_test):
                retval = self.consume(token_consume)
                break

        if retval is None:
            raise Exception(repr(self.buffer))
        self.consume('whitespace')

        return retval

    def consume_variable(self):
        return PlywoodVariableGrammar(self.buffer)

    def consume_whitespace(self):
        while self.buffer and self.test(self.whitespace):
            self.consume(self.whitespace)
            if self.whitespace == 'multiline_whitespace' and self.test('comment'):
                self.consume('comment')

    def consume_parens(self):
        location = self.buffer.position
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

        return PlywoodParens(location, tokens, is_set=is_set)

    def consume_list(self):
        location = self.buffer.position
        self.consume('list_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        tokens = []
        force_list = False
        is_slice = False
        while not self.test('list_close'):
            self.consume('whitespace')
            item = self.consume_until('comma_close_list')
            tokens.append(item)
            if self.test(','):
                force_list = True
                self.consume(',')
                self.consume('whitespace')
            elif self.test(':'):
                self.consume(':')
                self.consume('whitespace')
                is_slice = True
        self.consume('list_close')
        self.whitespace = prev_whitespace

        if is_slice:
            return PlywoodSlice(location, *tokens)
        else:
            return PlywoodList(location, tokens, force_list=force_list)

    def consume_xml(self):
        location = self.buffer.position
        self.consume('xml_open')
        element = self.consume('variable').plywood_value()
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'

        tokens = []
        while not self.test('xml_close'):
            self.consume('whitespace')
            item = self.consume_until('comma_close_xml')
            tokens.append(item)
            if self.test(','):
                self.consume(',')
                self.consume('whitespace')
        self.consume('xml_close')
        self.whitespace = prev_whitespace

        arguments = PlywoodParens(location, tokens)
        return PlywoodXml(location, element, arguments)

    def consume_dict(self):
        location = self.buffer.position
        self.consume('dict_open')
        prev_whitespace = self.whitespace
        self.whitespace = 'multiline_whitespace'
        self.consume('whitespace')

        tokens = []
        while not self.test('dict_close'):
            key = self.consume_until('colon_close_key')
            self.consume(':')

            self.consume('whitespace')
            value = self.consume_until('comma_close_dict')

            tokens.append(PlywoodKvp(key, value))
            if self.test(','):
                self.consume(',')
            self.consume('whitespace')
        self.consume('dict_close')
        self.whitespace = prev_whitespace

        return PlywoodDict(location, tokens)

    def consume_from(self):
        location = self.buffer.position
        from_var = self.consume('variable').plywood_value()
        self.consume('whitespace')

        module_name = self.consume('variable').plywood_value()
        self.consume('singleline_whitespace')
        Literal('import')(self.buffer)
        imports = self.convert_to_args(location, self.consume_until('eol', inline=True))

        parens = PlywoodParens(location, [module_name, imports])
        return PlywoodCallOperator(from_var, parens)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    TESTERS = {
        'eof': StringEnd().test,
        'eol': (Literal('\n') | '\r\n' | '\r' | '#' | StringEnd).test,
        'comment': Literal('#').test,
        'from': Literal('from').test,

        'variable': Char('_' + string.ascii_letters).test,
        'number': (Char('0123456789') | ('-' + Char('0123456789'))).test,
        'string': Char('"\'').test,

        'comma_close_parens': (Literal(',') | Literal(')')).test,
        'comma_close_list': (Literal(',') | Literal(']')).test,
        'comma_close_xml': (Literal(',') | Literal('>')).test,
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

        'xml_open': Literal('<'),
        'xml_close': Literal('>'),
        'parens_open': Literal('('),
        'parens_close': Literal(')'),
        'list_open': Literal('['),
        'list_close': Literal(']'),
        'dict_open': Literal('{'),
        'dict_close': Literal('}'),
        'block_open': Literal(':'),

        'singleline_whitespace': Chars(' \t'),
        'multiline_whitespace': Chars(' \t\r\n'),
        'optional_whitespace': Whitespace(' \t'),
    }

    MATCHERS.update({
        'eol': Optional(MATCHERS['comment']) + (Literal('\n') | '\r\n' | '\r' | StringEnd),
    })

    MATCHERS.update({
        'blankspace': Optional(MATCHERS['singleline_whitespace']) + Optional(MATCHERS['comment']),
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
