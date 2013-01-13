from chomsky import Whitespace, ParseException
from runtime import Runtime, Continue, SuppressNewline, SuppressOneNewline
from exceptions import PlywoodKeyError, this_line, BreakException, ContinueException
from functools import wraps


def check(check_type, error):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            retval = fn(*args, **kwargs)
            if not check_type(retval):
                raise Exception(error, fn, args[0])
            return retval
        return wrapper
    return decorator


class PlywoodValue(object):
    GLOBAL = {}
    RUNTIME = {}
    FUNCTIONS = {}
    PLUGINS = {}

    @classmethod
    def register(cls, name, value):
        cls.GLOBAL[name] = value

    @classmethod
    def register_runtime(cls, name=None, **kwargs):
        def decorator(fn):
            plugin_name = name
            if plugin_name is None:
                plugin_name = fn.__name__
            cls.RUNTIME[plugin_name] = (fn, kwargs)
            return fn
        return decorator

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
            retval = None
            for line in insides.splitlines():
                if retval is None:
                    retval = ''
                else:
                    retval += "\n"
                if line:
                    retval += current + line
            indent_pop()
            return retval

        scope['__indent'] = indent_apply
        scope.update(cls.GLOBAL)
        for key, runtime in cls.RUNTIME.iteritems():
            fn, kwargs = runtime
            value = PlywoodRuntime(fn, **kwargs)
            scope[key] = value
        for key, fn in cls.FUNCTIONS.iteritems():
            value = PlywoodFunction(fn)
            scope[key] = value
        for key, fn in cls.PLUGINS.iteritems():
            value = PlywoodPlugin(fn)
            scope[key] = value
        return scope

    def __init__(self, location):
        self.location = location

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'call values are wrong')
    def call(self, states, scope, arguments, block):
        return [Continue()], self

    def get_attr(self, scope, right):
        raise Exception("{self!r} has no property {right!r}".format(self=self, right=right))

    def plywood_value(self):
        return self

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        raise NotImplemented

    def get_value(self, scope):
        return self

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'run values are wrong')
    def run(self, states, scope):
        if Continue() in states:
            return [Continue()], self.get_value(scope)
        else:
            raise Exception(''.join(states))


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

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        states = [Continue()]
        return self.run(states, scope)[1].python_value(scope)

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        states = [Continue()]
        return self.run(states, scope)[1]

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'run values are wrong')
    def run(self, states, scope):
        retval = ''
        try:
            for cmd in self.lines:
                states, cmd_ret = cmd.run(states, scope)
                cmd_ret = str(cmd_ret.python_value(scope))
                if len(cmd_ret):
                    retval += cmd_ret
                    suppress_newline = SuppressNewline() in states or SuppressOneNewline() in states
                    if not self.inline and not suppress_newline:
                        retval += "\n"
                    try:
                        states.remove(SuppressOneNewline())
                    except ValueError:
                        pass
        except (BreakException, ContinueException) as e:
            raise type(e)(retval)

        try:
            states.remove(SuppressNewline())
        except ValueError:
            pass
        return states, PlywoodString(self.location, retval)


class PlywoodVariable(PlywoodValue):
    def __init__(self, location, name):
        self.name = name
        super(PlywoodVariable, self).__init__(location)

    def get_name(self):
        return self.name

    def set_id(self, scope, var):
        return self.get_value(scope).set_id(scope, var)

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        try:
            retval = scope[self.name]
            if not isinstance(retval, PlywoodValue):
                retval = PlywoodWrapper(self.location, retval)
                scope[self.name] = retval
            retval.location = self.location
            return retval
        except KeyError:
            line_no, line = this_line(scope['__input'], self.location)
            raise PlywoodKeyError(line_no, line)

    def get_attr(self, scope, right):
        return self.get_value(scope).get_attr(scope, right)

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

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.value

    def __eq__(self, other):
        return self.value == str(other)

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        return self.value
        value = self.value
        if self.triple:
            return '''"""{lang}\n{value}\n"""'''.format(lang=self.lang, value=value)
        return repr(value)


class PlywoodPythonValue(PlywoodValue):
    def __init__(self, location, value):
        self.value = value
        super(PlywoodPythonValue, self).__init__(location)

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.value

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        return str(self.value)


class PlywoodNumber(PlywoodValue):
    def __init__(self, location, value):
        self.value = value
        super(PlywoodNumber, self).__init__(location)

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
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
        return PlywoodWrapper(left.location, handler(left, right, scope))

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        super(PlywoodOperator, self).__init__(left.location)

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        return self.handle(self.operator, self.left, self.right, scope)

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

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

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'run values are wrong')
    def run(self, states, scope):
        if Continue() in states:
            retval = self.left.get_value(scope).call(states, scope, self.right, self.block)
            return retval
        else:
            raise Exception(''.join(states))

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        return self.run([Continue()], scope)[1]

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
            handler = cls.OPERATORS[operator.operator]
        except KeyError:
            raise Exception('No operator handler for {operator!r}'.format(self=operator))
        return PlywoodWrapper(operator.location, handler(value, scope))

    def __init__(self, location, operator, value):
        self.operator = operator
        self.value = value
        super(PlywoodUnaryOperator, self).__init__(location)

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        return self.handle(self, self.value, scope)

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
        is_not_kvp = lambda value: not isinstance(value, PlywoodKvp)
        self.args = filter(is_not_kvp, values)
        self.kwargs = filter(is_kvp, values)
        self.is_set = is_set
        super(PlywoodParens, self).__init__(location)

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        return self.args[0].get_value(scope)

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.args[0].python_value(scope)

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
    def __init__(self, location, values, force_list=False):
        self.values = values
        self.force_list = force_list
        super(PlywoodList, self).__init__(location)

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.values

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

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return dict((kvp.key.python_value(scope), kvp.value.python_value(scope)) for kvp in self.values)

    def get_item(self, scope, right):
        key = right.python_value(scope)
        for kvp in self.values:
            if kvp.key.python_value(scope) == key:
                return kvp.value
        raise KeyError(key)

    def get_attr(self, scope, right):
        key = right.get_name()
        for kvp in self.values:
            if kvp.key.python_value(scope) == key:
                return kvp.value
        raise KeyError(key)
        # if not isinstance(src, PlywoodValue):
        #     key = right.get_name()
        #     if hasattr(src, key):
        #         return getattr(src, key)
        #     else:
        #         return src[key]
        # else:
        #     return src.get_attr(scope, right)

    def __repr__(self):
        return type(self).__name__ + '{' + ', '.join(repr(v) for v in self.values) + '}'

    def __str__(self):
        return '{' + ', '.join(repr(v) for v in self.values) + '}'


class PlywoodCallable(PlywoodValue):
    def __init__(self, fn, block=False):
        self.fn = fn
        self.accepts_block = block

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'run values are wrong')
    def run(self, states, scope):
        if not hasattr(self, 'location'):
            raise Exception(repr(self) + ' has no location')
        arguments = PlywoodParens(self.location, [])
        block = PlywoodBlock(self.location, [])
        if Continue() in states:
            return self.call(states, scope, arguments, block)
        else:
            return None

    @check(lambda ret: not isinstance(ret, PlywoodValue), 'Must be a python value')
    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

    @check(lambda ret: isinstance(ret, PlywoodValue), 'Must be a PlywoodValue')
    def get_value(self, scope):
        return self.run([Continue()], scope)[1]

    def __str__(self):
        return '<{type.__name__}:{name}>'.format(type=type(self), name=self.fn.__name__)

    def __repr__(self):
        return '<{type.__name__}:{name}>'.format(type=type(self), name=self.fn.__name__)


class PlywoodRuntime(PlywoodCallable):
    '''
    Runtime plugins are things like ``if``, ``for``, ``while``, and other
    language constructs.
    '''
    def __init__(self, fn, accepts=[Continue()], suppress_newline=True):
        if not isinstance(accepts, list):
            accepted_states = [accepts]
        else:
            accepted_states = accepts

        self.fn = fn
        self.accepts_states = accepted_states
        self.suppress_newline = suppress_newline

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'call values are wrong')
    def call(self, states, scope, arguments, block):
        if any(state in states for state in self.accepts_states):
            states, retval = self.fn(states, scope, arguments, block)
            if self.suppress_newline:
                states.append(SuppressOneNewline())
            return PlywoodWrapper(self.location, [states, retval])
        states.append(SuppressOneNewline())
        return states, PlywoodWrapper(self.location, '')


class PlywoodPlugin(PlywoodCallable):
    def __init__(self, fn):
        self.fn = fn
        self.id = None
        self.classes = []

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'call values are wrong')
    def call(self, states, scope, arguments, block):
        return [Continue()], PlywoodWrapper(self.location, self.fn(scope, arguments, block, self.classes, self.id))

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


class PlywoodFunction(PlywoodCallable):
    def __init__(self, fn, block=False):
        self.fn = fn
        self.accepts_block = block

    @check(lambda run: len(run) == 2 and isinstance(run[1], PlywoodValue), 'call values are wrong')
    def call(self, states, scope, arguments, block):
        args = (arg.get_value(scope).python_value(scope) for arg in arguments.args)
        kwargs = dict(
            (item.key.get_value(scope).python_value(scope), item.value.get_value(scope).python_value(scope))
                for item in arguments.kwargs
                )
        if self.accepts_block:
            retval = self.fn(block, *args, **kwargs)
        else:
            retval = self.fn(*args, **kwargs)
        return [Continue()], PlywoodWrapper(self.location, retval)


def PlywoodWrapper(location, value):
    if isinstance(value, PlywoodValue):
        return value
    if (isinstance(value, list) or isinstance(value, tuple)) \
        and len(value) == 2 \
        and (isinstance(value[0], list) or isinstance(value[0], tuple)) \
        and len(value[0]) > 0 \
        and isinstance(value[0][0], Runtime):
        return [value[0], PlywoodWrapper(location, value[1])]
    if isinstance(value, str) or isinstance(value, unicode):
        return PlywoodString(location, value)
    if isinstance(value, int) or isinstance(value, long) or isinstance(value, float):
        return PlywoodNumber(location, value)
    if isinstance(value, list):
        return PlywoodList(location, value)
    if isinstance(value, dict):
        values = []
        for key, value in value.iteritems():
            key = PlywoodWrapper(location, key)
            value = PlywoodWrapper(location, value)
            values.append(PlywoodKvp(key, value))
        return PlywoodDict(location, values)
    return PlywoodPythonValue(location, value)
