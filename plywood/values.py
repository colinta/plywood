from chomsky import Whitespace


class PlywoodValue(object):
    def to_value(self):
        return self


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

    def run(self):
        retval = ''
        for cmd in self.lines:
            retval += str(cmd)
        return retval


class PlywoodVariable(PlywoodValue):
    def __init__(self, name):
        self.name = name

    def get_value(self, scope):
        return scope[self.name]

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

    def get_value(self, scope):
        return self.value

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

    def get_value(self, scope):
        return self.value

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

    def get_value(self):
        return self.left.get_value() + self.right.get_value()

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

    def get_value(self):
        return self.scope[self.left.get_value()](*self.right.values)

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
