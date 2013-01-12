from chomsky import Whitespace, ParseException
from runtime import Continue
from exceptions import PlywoodKeyError, this_line


class PlywoodValue(object):
    GLOBAL = {}
    FUNCTIONS = {}
    PLUGINS = {}

    @classmethod
    def register(cls, name, value):
        cls.GLOBAL[name] = value

    @classmethod
    def register_fn(cls, name=None):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.FUNCTIONS[plugin_name] = fn
            return fn
        return decorator

    @classmethod
    def register_plugin(cls, name=None):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.PLUGINS[plugin_name] = fn
            return fn
        return decorator

    @classmethod
    def new_scope(cls, options, input, self_scope):
        scope = {}
        scope['__input'] = input
        add_indent = options.get('indent', '    ')
        scope['self'] = self_scope  # TODO: PlywoodWrapper
        indent = ['']

        def indent_push(new_indent=add_indent):
            indent.append(new_indent)
            return indent

        def indent_pop():
            return indent.pop()

        def indent_apply(insides):
            if not insides:
                return insides
            indent_push()
            current = indent[-1]
            retval = current + insides.replace("\n", "\n" + current)
            indent_pop()
            return retval

        scope['__indent'] = indent_apply
        scope.update(cls.GLOBAL)
        for key, fn in cls.FUNCTIONS.iteritems():
            value = PlywoodCallOperatorable(fn)
            scope[key] = value
        for key, fn in cls.PLUGINS.iteritems():
            value = PlywoodPlugin(fn)
            scope[key] = value
        return scope

    def __init__(self, location):
        self.location = location

    def get(self, scope):
        return self.get_value(scope)

    def get_attr(self, scope, right):
        raise Exception("{self!r} has no property {right!r}".format(self=self, right=right))

    def to_value(self):
        return self

    def run(self, state, scope):
        if state == Continue():
            return Continue(), self.get_value(scope)
        else:
            return None


class PlywoodBlock(PlywoodValue):
    def __init__(self, location, lines, inline=False):
        self.lines = lines
        self.inline = inline
        super(PlywoodBlock, self).__init__(location)

    def append(self, line):
        self.lines.append(line)

    def __getitem__(self, key):
        return self.lines.__getitem__(key)

    def __eq__(self, other):
        return self is other or \
            isinstance(other, list) and other == self.lines

    def __repr__(self):
        return type(self).__name__ + '(\n' + '\n'.join(repr(v) for v in self.lines) + '\n)'

    def __str__(self):
        return '\n'.join(str(v) for v in self.lines)

    def get_value(self, scope):
        state, retval = self.run(scope)
        return retval

    def run(self, scope):
        retval = ''
        state = Continue()
        for cmd in self.lines:
            state, cmd_ret = cmd.run(state, scope)
            if isinstance(cmd_ret, Continue):
                raise Exception('h')
            if state != Continue():
                raise Exception('hell')
            else:
                if isinstance(cmd_ret, PlywoodValue):
                    cmd_ret = cmd_ret.get_value(scope)
                cmd_ret = str(cmd_ret)
                retval += cmd_ret
                if not self.inline and cmd_ret:
                    retval += "\n"
        return state, retval


class PlywoodVariable(PlywoodValue):
    def __init__(self, location, name):
        self.name = name
        super(PlywoodVariable, self).__init__(location)

    def get_name(self):
        return self.name

    def set_id(self, scope, var):
        return self.get(scope).set_id(scope, var)

    def get_value(self, scope):
        return self.get(scope).get_value(scope)

    def get(self, scope):
        try:
            retval = scope[self.name]
        except KeyError:
            line_no, line = this_line(scope['__input'], self.location)
            raise PlywoodKeyError(line_no, line)
        retval.location = self.location
        return retval

    def get_attr(self, scope, right):
        src = scope[self.name]
        # src.location = self.location
        if not isinstance(src, PlywoodValue):
            key = right.get_name()
            if hasattr(src, key):
                return getattr(src, key)
            else:
                return src[key]
        else:
            return src.get_attr(scope, right)

    def __eq__(self, other):
        return isinstance(other, PlywoodVariable) and other.name == self.name

    def __repr__(self):
        return '{type.__name__}({self.name})'.format(type=type(self), self=self)

    __str__ = lambda self: self.name


class PlywoodString(PlywoodValue):
    def __init__(self, location, value, triple=False):
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
        super(PlywoodString, self).__init__(location)

    def get_name(self):
        return self.value

    def get_value(self, scope):
        return self.value

    def __eq__(self, other):
        return self.value == str(other)

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        value = self.value
        if self.triple:
            return '''"""{lang}\n{value}\n"""'''.format(lang=self.lang, value=value)
        return repr(value)


class PlywoodNumber(PlywoodValue):
    def __init__(self, location, value):
        self.value = value
        super(PlywoodNumber, self).__init__(location)

    def get_value(self, scope):
        return self.value

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        return str(self.value)


class PlywoodOperator(PlywoodValue):
    INDENT = ''
    OPERATORS = {}

    @classmethod
    def register(cls, operator):
        def decorator(fn):
            cls.OPERATORS[operator] = fn
            return fn
        return decorator

    @classmethod
    def handle(cls, operator, left, right, scope):
        try:
            handler = cls.OPERATORS[operator]
        except KeyError:
            raise Exception('No operator handler for {operator!r}'.format(self=operator))
        return handler(left, right, scope)

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        super(PlywoodOperator, self).__init__(left.location)

    def get_value(self, scope):
        return self.handle(self.operator, self.left, self.right, scope)

    def get_attr(self, scope, right):
        return self.get_value(scope).get_attr(scope, right)

    def __repr__(self):
        indent = type(self).INDENT
        type(self).INDENT += '  '
        retval = '{indent}{type.__name__}({self.left!r}\n{indent}  {self.operator!r}\n{indent}  {self.right!r}\n{indent})\n'.format(type=type(self), self=self, indent=indent)
        type(self).INDENT = indent
        return retval

    def __str__(self):
        op = str(self.operator)
        if self.operator == '[]':
            return '{self.left}[{self.right}]'.format(self=self)
        if self.operator not in ['.', '@']:
            op = ' ' + op + ' '
        return '{self.left}{op}{self.right}'.format(self=self, op=op)


class PlywoodCallOperator(PlywoodOperator):
    def __init__(self, left, right, block=None):
        super(PlywoodCallOperator, self).__init__('()', left, right)
        if not block:
            block = PlywoodBlock(-1, [])
        self.block = block

    def run(self, state, scope):
        if state == Continue():
            return self.left.get(scope).call(scope, self.right, self.block)
        else:
            return None

    def get(self, scope):
        return self.left.get(scope)

    def get_value(self, scope):
        return self.run(Continue(), scope)[1]

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
        retval = '{indent}{self.left}{self.right}'.format(self=self, indent=indent)
        if self.block:
            retval += ':\n{indent}    {block}'.format(self=self, block=str(self.block).replace("\n", "\n    " + indent), indent=indent)
        return retval


class PlywoodUnaryOperator(PlywoodValue):
    OPERATORS = {}

    @classmethod
    def register(cls, operator):
        def decorator(fn):
            cls.OPERATORS[operator] = fn
            return fn
        return decorator

    @classmethod
    def handle(cls, operator, value, scope):
        try:
            handler = cls.OPERATORS[operator]
        except KeyError:
            raise Exception('No operator handler for {operator!r}'.format(self=operator))
        return handler(value, scope)

    def __init__(self, location, operator, value):
        self.operator = operator
        self.value = value
        super(PlywoodUnaryOperator, self).__init__(location)

    def get_value(self, scope):
        return self.handle(self.operator, self.value, scope)

    def __repr__(self):
        return '{type.__name__}({self.operator!r}, {self.value!r})'.format(type=type(self), self=self)


class PlywoodParens(PlywoodValue):
    def __init__(self, location, values, is_set=False):
        def convert_assign(value):
            if isinstance(value, PlywoodOperator) and value.operator == '=':
                # convert the 'variable' into a string
                if not isinstance(value.left, PlywoodVariable):
                    raise ParseException('Invalid keyword argument')
                key = PlywoodString(value.location, value.left.name)
                return PlywoodKvp(key, value.right, kwarg=True)
            return value

        values = map(convert_assign, values)
        is_kvp = lambda value: isinstance(value, PlywoodKvp)
        not_is_kvp = lambda value: not isinstance(value, PlywoodKvp)
        self.args = filter(not_is_kvp, values)
        self.kwargs = filter(is_kvp, values)
        self.is_set = is_set
        super(PlywoodParens, self).__init__(location)

    def get_value(self, scope):
        return self.args[0].get_value(scope)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.args[key]
        return self.kwargs[key]

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
    def __init__(self, location, values, force_list):
        self.values = values
        self.force_list = force_list
        super(PlywoodList, self).__init__(location)

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '[' + ', '.join(repr(v) for v in self.values) + ']'

    def __str__(self):
        return '[' + ', '.join(str(v) for v in self.values) + ']'


class PlywoodIndices(PlywoodValue):
    def __init__(self, location, values, force_list):
        self.values = values
        self.force_list = force_list
        super(PlywoodIndices, self).__init__(location)

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '[' + ', '.join(repr(v) for v in self.values) + ']'

    def __str__(self):
        return ', '.join(str(v) for v in self.values) + (self.force_list and ',' or '')


class PlywoodSlice(PlywoodValue):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        super(PlywoodSlice, self).__init__(self.start.location)

    def __repr__(self):
        return type(self).__name__ + '({self.start!r}:{self.stop!r})'.format(self=self)

    def __str__(self):
        return '{self.start}:{self.stop}'.format(self=self)


class PlywoodDict(PlywoodValue):
    def __init__(self, location, values):
        self.values = values
        super(PlywoodDict, self).__init__(location)

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '{' + ', '.join(repr(v) for v in self.values) + '}'

    def __str__(self):
        return '{' + ', '.join(repr(v) for v in self.values) + '}'


class PlywoodCallOperatorable(PlywoodValue):
    def __init__(self, fn, block=False):
        self.fn = fn
        self.accepts_block = block

    def run(self, state, scope):
        if not hasattr(self, 'location'):
            raise Exception(repr(self) + ' has no location')
        arguments = PlywoodParens(self.location, [])
        block = PlywoodBlock(self.location, [])
        if state == Continue():
            return self.call(scope, arguments, block)
        else:
            return None

    def get_value(self, scope):
        return self.run(Continue(), scope)[1]

    def call(self, scope, arguments, block):
        args = (arg.get_value(scope) for arg in arguments.args)
        kwargs = dict(
            (item.key.get_value(scope), item.value.get_value(scope))
                for item in arguments.kwargs
                )
        if self.accepts_block:
            retval = self.fn(block, *args, **kwargs)
        else:
            retval = self.fn(*args, **kwargs)
        return Continue(), retval

    def __str__(self):
        raise Exception('')
        return '<{type.__name__}:{name}>'.format(type=type(self), name=self.fn.__name__)

    def __repr__(self):
        return '<{type.__name__}:{name}>'.format(type=type(self), name=self.fn.__name__)


class PlywoodPlugin(PlywoodCallOperatorable):
    def __init__(self, fn):
        self.fn = fn
        self.id = None
        self.classes = []

    def call(self, scope, arguments, block):
        return Continue(), self.fn(scope, arguments, block, self.classes, self.id)

    def copy(self):
        copy = type(self)(self.fn)
        copy.id = self.id
        copy.classes.extend(self.classes)
        if hasattr(self, 'location'):
            copy.location = self.location
        return copy

    def get_attr(self, scope, right):
        copy = self.copy()
        copy.classes.append(right.get_name())
        return copy

    def set_id(self, scope, var):
        copy = self.copy()
        copy.id = var.get_name()
        return copy


class PlywoodCallOperatorable(PlywoodValue):
    def __init__(self, fn, block=False):
        self.fn = fn
        self.accepts_block = block

    def run(self, state, scope):
        if not hasattr(self, 'location'):
            raise Exception(repr(self) + ' has no location')
        arguments = PlywoodParens(self.location, [])
        block = PlywoodBlock(self.location, [])
        if state == Continue():
            return self.call(scope, arguments, block)
        else:
            return None

    def get_value(self, scope):
        return self.run(Continue(), scope)[1]

    def call(self, scope, arguments, block):
        args = (arg.get_value(scope) for arg in arguments.args)
        kwargs = dict(
            (item.key.get_value(scope), item.value.get_value(scope))
                for item in arguments.kwargs
                )
        if self.accepts_block:
            retval = self.fn(block, *args, **kwargs)
        else:
            retval = self.fn(*args, **kwargs)
        return Continue(), retval

    def __str__(self):
        raise Exception('')
        return '<{type.__name__}:{name}>'.format(type=type(self), name=self.fn.__name__)

    def __repr__(self):
        return '<{type.__name__}:{name}>'.format(type=type(self), name=self.fn.__name__)
