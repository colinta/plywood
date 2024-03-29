from chomsky import Whitespace, ParseException
from .runtime import Runtime, Continue, Skip, SuppressNewline, SuppressOneNewline
from .exceptions import KeyError as PlywoodKeyError, BreakException, ContinueException, InvalidArguments, PlywoodRuntimeError
from .element import output_element
from .util import uniq_by


class PlywoodValue(object):
    def __init__(self, location):
        self.location = location
        self.suppress_nl = False

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location)
        else:
            copy = instance
        copy.suppress_nl = self.suppress_nl
        return copy

    def get_attr(self, attr, scope):
        raise PlywoodRuntimeError(self.location, scope, "{self!r} has no property {attr!r}".format(self=self, attr=attr))

    def assign_id(self, attr, scope):
        raise PlywoodRuntimeError(self.location, scope, "{self!r} does not suppport id assignment {attr!r}".format(self=self, attr=attr))

    def plywood_value(self):
        return self

    def python_value(self, scope):
        raise NotImplementedError

    def get_value(self, scope):
        return self

    def call(self, states, scope, arguments, block):
        if len(block.lines):
            raise PlywoodRuntimeError(self.location, scope, '{0!s} does not support block argument'.format(self))
        if len(arguments.args) != 1 \
            or len(arguments.kwargs):
            raise PlywoodRuntimeError(self.location, scope, '{0!s} only accepts one conditional argument'.format(self))
        retval = str(self.python_value(scope)) + str(arguments.args[0].python_value(scope))
        return [Continue()], PlywoodWrapper(self.location, retval)

    def run(self, states, scope):
        if Continue() in states:
            if self.suppress_nl:
                states.append(SuppressOneNewline())
            return states, self.get_value(scope)
        else:
            raise PlywoodRuntimeError(self.location, scope, ''.join(states))


class PlywoodBlock(PlywoodValue):
    def __init__(self, location, lines, inline=False):
        self.lines = lines
        self.inline = inline
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, list(line.copy() for line in self.lines), self.inline)
        else:
            copy = instance
        return super().copy(copy)

    def append(self, line):
        self.lines.append(line)

    def __getitem__(self, key):
        return self.lines.__getitem__(key)

    def __len__(self):
        return len(self.lines)

    def __eq__(self, other):
        return self is other or \
            isinstance(other, list) and other == self.lines

    def __repr__(self):
        return type(self).__name__ + '(\n' + '\n'.join(repr(v) for v in self.lines) + '\n)'

    def __str__(self):
        return '\n'.join(str(v) for v in self.lines)

    def python_value(self, scope):
        states = [Continue()]
        return self.run(states, scope)[1].python_value(scope)

    def get_value(self, scope):
        states = [Continue()]
        return self.run(states, scope)[1]

    def run(self, states, scope):
        retval = ''
        try:
            for cmd in self.lines:
                states, cmd_ret = cmd.run(states, scope)
                # commands that *do* return a value, but do not want that value
                # output, e.g. assignments.
                if Skip() in states:
                    states.remove(Skip())
                    states.append(Continue())
                else:
                    cmd_ret = cmd_ret.python_value(scope)
                    if cmd_ret is not None:
                        retval += str(cmd_ret)
                        suppress_newline = SuppressNewline() in states or SuppressOneNewline() in states
                        if not self.inline and not suppress_newline:
                            retval += scope['__env'].options['separator']
                        try:
                            states.remove(SuppressOneNewline())
                        except ValueError:
                            pass
        except (BreakException, ContinueException) as e:
            # store the current output, because it is still relevant!
            # plugins that support break and continue should return this string
            raise type(e)(retval)

        try:
            states.remove(SuppressNewline())
        except ValueError:
            pass
        return states, PlywoodString(self.location, retval)


class PlywoodVariable(PlywoodValue):
    def __init__(self, location, name):
        self.name = name
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, self.name)
        else:
            copy = instance
        return super().copy(copy)

    def run(self, states, scope):
        return self.get_value(scope).run(states, scope)

    def call(self, states, scope, arguments, block):
        return self.get_value(scope).call(states, scope, arguments, block)

    def get_name(self):
        return self.name

    def set_attr(self, attr, value, scope):
        scope[self.name] = value

    def set_item(self, attr, value, scope):
        scope[self.name] = value

    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

    def get_value(self, scope):
        try:
            retval = scope[self.name]
        except KeyError:
            retval = PlywoodPythonValue(self.location, None)

        if not isinstance(retval, PlywoodValue):
            retval = PlywoodWrapper(self.location, retval)
            scope[self.name] = retval
        else:
            retval.location = self.location
        return retval

    def get_attr(self, attr, scope):
        return self.get_value(scope).get_attr(attr, scope)

    def assign_id(self, attr, scope):
        return self.get_value(scope).assign_id(attr, scope)

    def get_item(self, attr, scope):
        return self.get_value(scope).get_item(attr, scope)

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
            # unindent, and parse language
            lang, value = PlywoodString.unindent(value, return_lang=True)
            self.lang = lang

        if isinstance(value, str):
            self.value = value
        else:
            self.value = value.decode('utf-8')
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, self.value, self.triple)
        else:
            copy = instance
        return super().copy(copy)

    @staticmethod
    def unindent(value, return_lang=False):
        indent = None
        lines = value.splitlines()
        lang = ''
        if return_lang and len(lines) > 1:
            lang = lines.pop(0)
        # pop off the last line if it is empty
        if lines and lines[-1] == '':
            lines.pop()

        for line in lines:
            if not line:
                continue
            whitespace = str(Whitespace(' \t')(line))
            if indent is None:
                indent = whitespace
            else:
                new_indent = ''
                for index, w in enumerate(whitespace[:len(indent)]):
                    if w == indent[index]:
                        new_indent += w
                    else:
                        break
            if not indent:
                break
        if indent:
            lines = map(lambda line: line[len(indent):], lines)
        value = "\n".join(lines)
        if return_lang:
            return lang, value
        return value

    def get_name(self):
        return self.value

    def get_value(self, scope):
        return self

    def python_value(self, scope):
        from .run import Plywood
        from .env import PlywoodEnv

        # string interpolation
        original = self.value
        retval = ''
        index = 0
        was_open_bracket = False
        consuming = False
        was_close_bracket = False
        inside = ''
        if '__env' in scope:
            env = scope['__env']
        else:
            env = PlywoodEnv({'separator': ' '})
        scope.push()
        context = scope.get('self', {})
        while index < len(original):
            c = original[index]
            if consuming and was_close_bracket and c == '}':
                consuming = False
                was_close_bracket = False
                inside = PlywoodString.unindent(inside)
                retval += Plywood(inside).run(context, env).rstrip()
                inside = ''
            elif consuming and c == '}':
                was_close_bracket = True
            elif consuming:
                if was_close_bracket:
                    inside += '}'
                    was_close_bracket = False
                inside += c
            elif c == '{' and was_open_bracket:
                was_open_bracket = False
                consuming = True
            elif c == '{':
                was_open_bracket = True
            else:
                if was_open_bracket:
                    retval += '{'
                    was_open_bracket = False
                retval += c
            index += 1
        if was_open_bracket:
            raise ParseException("Unclosed '{{'")
        scope.pop()
        return retval

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
        if callable(value):
            raise Exception('hey now')
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, self.value)
        else:
            copy = instance
        return super().copy(copy)

    def python_value(self, scope):
        return self.value

    def set_attr(self, attr, value, scope):
        setattr(self.value, attr.get_name(), value.python_value(scope))

    def get_attr(self, attr, scope):
        val = self.python_value(scope)
        attr = attr.get_name()
        if hasattr(val, attr):
            return getattr(val, attr)
        try:
            return val[attr]
        except (KeyError, TypeError):
            pass
        return None

    def set_item(self, attr, value, scope):
        self.value[attr.get_name()] = value.python_value(scope)

    def get_item(self, attr, scope):
        val = self.python_value(scope)
        key = attr.python_value(scope)
        try:
            return val[key]
        except IndexError:
            pass
        except KeyError:
            pass
        return None

    def __repr__(self):
        return '{type.__name__}({self.value!r})'.format(type=type(self), self=self)

    def __str__(self):
        return str(self.value)


class PlywoodNumber(PlywoodValue):
    def __init__(self, location, value):
        self.value = value
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, self.value)
        else:
            copy = instance
        return super().copy(copy)

    def call(self, states, scope, arguments, block):
        if len(block.lines):
            raise InvalidArguments('{0!s} does not support block argument'.format(self))
        if len(arguments.args) != 1 \
            or len(arguments.kwargs):
            raise InvalidArguments('{0!s} only accepts one conditional argument'.format(self))
        retval = self.python_value(scope) * arguments.args[0].python_value(scope)
        return [Continue()], PlywoodWrapper(self.location, retval)

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
    def register(cls, operator, **kwargs):
        def decorator(fn):
            cls.OPERATORS[operator] = (fn, kwargs)
            return fn
        return decorator

    @classmethod
    def handle(cls, operator, left, right, scope):
        try:
            handler, _ = cls.OPERATORS[operator]
        except KeyError:
            raise PlywoodRuntimeError(self.location, scope, 'No operator handler for {operator!r}'.format(operator=operator))
        try:
            return PlywoodWrapper(left.location, handler(left, right, scope))
        except Exception as e:
            message = str(e)
        raise PlywoodRuntimeError(left.location, scope, message)

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        if left == '()':
            raise Exception('foo')
        super().__init__(left.location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.operator, self.left.copy(), self.right.copy())
        else:
            copy = instance
        return super().copy(copy)

    def run(self, states, scope):
        try:
            _, kwargs = self.OPERATORS[self.operator]
        except KeyError:
            kwargs = {}

        if Continue() in states:
            states = [kwargs.get('state') or Continue()]
            return states, self.get_value(scope)
        else:
            raise PlywoodRuntimeError(self.location, scope, ''.join(states))

    def get_value(self, scope):
        return self.handle(self.operator, self.left, self.right, scope)

    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

    def get_attr(self, attr, scope):
        return self.handle(self.operator, self.left, self.right, scope).get_attr(attr, scope)

    def assign_id(self, attr, scope):
        return self.handle(self.operator, self.left, self.right, scope).assign_id(attr, scope)

    def get_item(self, attr, scope):
        target = self.handle(self.operator, self.left, self.right, scope)
        return target.get_item(attr, scope)

    def set_attr(self, attr, value, scope):
        try:
            handler, kwargs = self.OPERATORS[self.operator]
        except KeyError:
            raise PlywoodRuntimeError(self.location, scope, 'No operator handler for {operator!r}'.format(operator=self.operator))
        try:
            setter = kwargs['setter']
        except KeyError:
            raise PlywoodRuntimeError(self.location, scope, 'Operator {operator!r} cannot set values'.format(operator=self.operator))
        return setter(self, attr, value, scope)

    def set_item(self, attr, value, scope):
        try:
            handler, kwargs = self.OPERATORS[self.operator]
        except KeyError:
            raise PlywoodRuntimeError(self.location, scope, 'No operator handler for {operator!r}'.format(operator=self.operator))
        try:
            setter = kwargs['setter']
        except KeyError:
            raise PlywoodRuntimeError(self.location, scope, 'Operator {operator!r} cannot set values'.format(operator=self.operator))
        return setter(self, attr, value, scope)

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
        if self.operator not in ['.']:
            op = ' ' + op + ' '
        return '{self.left}{op}{self.right}'.format(self=self, op=op)


class PlywoodCallOperator(PlywoodOperator):
    def __init__(self, left, right, block=None):
        if not block:
            block = PlywoodBlock(-1, [])
        self.block = block
        super().__init__('()', left, right)

    def copy(self, instance=None):
        left = self.left.copy()
        right = self.right.copy()
        block = self.block.copy()
        if instance is None:
            copy = type(self)(left, right, block)
        else:
            copy = instance
        return super().copy(copy)

    def run(self, states, scope):
        if Continue() in states:
            return self.left.get_value(scope).call(states, scope, self.right, self.block)
        else:
            raise PlywoodRuntimeError(self.location, scope, ''.join(states))

    def call(self, states, scope, arguments, block):
        return self.left.get_value(scope).run(states, scope)

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
    def register(cls, operator, **kwargs):
        def decorator(fn):
            cls.OPERATORS[operator] = (fn, kwargs)
            return fn
        return decorator

    @classmethod
    def handle(cls, operator, value, scope):
        try:
            handler, _ = cls.OPERATORS[operator.operator]
        except KeyError:
            raise PlywoodRuntimeError(self.location, scope, 'No operator handler for {operator!r}'.format(self=operator))
        return PlywoodWrapper(operator.location, handler(value, scope))

    def __init__(self, location, operator, value):
        self.operator = operator
        self.value = value
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, self.operator, self.value.copy())
        else:
            copy = instance
        return super().copy(copy)

    def get_value(self, scope):
        return self.handle(self, self.value, scope)

    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

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
        def kvp_name(value):
            if isinstance(value.key, PlywoodVariable):
                return value.name
            if isinstance(value.key, PlywoodString):
                return value.key.value
            return None

        is_kvp = lambda value: isinstance(value, PlywoodKvp)
        is_not_kvp = lambda value: not isinstance(value, PlywoodKvp)
        values = list(map(convert_assign, values))
        self.args = list(filter(is_not_kvp, values))
        self.kwargs = list(uniq_by(filter(is_kvp, values), kvp_name))
        self.is_set = is_set
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, [], self.is_set)
        else:
            copy = instance
        copy.args = list(value.copy() for value in self.args)
        copy.kwargs = list(value.copy() for value in self.kwargs)
        return super().copy(copy)

    def get_value(self, scope):
        return self.args[0].get_value(scope)

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
        between = ''
        if self.args and self.kwargs:
            between = ', '
        return type(self).__name__ + '(' + ', '.join(repr(v) for v in self.args) + between + ', '.join(repr(v) for v in self.kwargs) + extra + ')'

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
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, list(value.copy() for value in self.values), self.force_list)
        else:
            copy = instance
        return super().copy(copy)

    def python_value(self, scope):
        return self.values

    def get_item(self, index, scope):
        index = index.python_value(scope)
        sys.stderr.write(repr(index))
        try:
            return val[index]
        except (KeyError, TypeError):
            pass

    def get_attr(self, attr, scope):
        attr = attr.get_name()
        if hasattr(self.values, attr):
            return getattr(self.values, attr)
        try:
            return val[attr]
        except (KeyError, TypeError):
            pass
        return None

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __repr__(self):
        return type(self).__name__ + '[' + ', '.join(repr(v) for v in self.values) + ']'

    def __str__(self):
        return '[' + ', '.join(str(v) for v in self.values) + ']'


class PlywoodXml(PlywoodValue):
    def __init__(self, location, element, arguments):
        self.element = element
        self.arguments = arguments
        self.location = location

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, self.element.copy(), self.arguments.copy())
        else:
            copy = instance
        return super().copy(copy)

    def run(self, states, scope):
        if not hasattr(self, 'location'):
            raise PlywoodRuntimeError(self.location, scope, repr(self) + ' has no location')
        arguments = PlywoodParens(self.location, [])
        block = PlywoodBlock(self.location, [])
        if Continue() in states:
            return self.call(states, scope, arguments, block)
        else:
            return None

    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

    def call(self, states, scope, arguments, block):
        if Continue() in states:
            is_self_closing = not block
            return [Continue()], PlywoodWrapper(self.location, output_element(scope, self.arguments, block, tag_name=self.element.get_name(), classes=[], id_name=None, is_self_closing=is_self_closing))
        else:
            raise PlywoodRuntimeError(self.location, scope, ''.join(states))

    def __repr__(self):
        return type(self).__name__ + '<' + repr(self.element) + ' ' + ', '.join(repr(v) for v in self.arguments) + '>'

    def __str__(self):
        return '<' + self.element + ' ' + ', '.join(str(v) for v in self.arguments) + '>'


class PlywoodIndices(PlywoodValue):
    def __init__(self, location, values, force_list):
        self.values = values
        self.force_list = force_list
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, list(value.copy() for value in self.values), self.force_list)
        else:
            copy = instance
        return super().copy(copy)

    def get_value(self, scope):
        if len(self.values) > 1:
            raise PlywoodRuntimeError(self.location, scope, "{self!r} is not a valid index".format(self=self))
        return self.values[0].get_value(scope)

    def python_value(self, scope):
        if self.force_list:
            return [value.python_value(scope) for value in self.values]
        return self.values[0].python_value(scope)

    def get_name(self):
        return self.values[0].get_name()

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
        super().__init__(self.start.location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.start.copy(), self.stop.copy())
        else:
            copy = instance
        return super().copy(copy)

    def python_value(self, scope):
        raise NotImplementedError

    def __repr__(self):
        return type(self).__name__ + '({self.start!r}:{self.stop!r})'.format(self=self)

    def __str__(self):
        return '{self.start}:{self.stop}'.format(self=self)


class PlywoodDict(PlywoodValue):
    def __init__(self, location, values):
        self.values = values
        super().__init__(location)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.location, list(value.copy() for value in self.values))
        else:
            copy = instance
        return super().copy(copy)

    def python_value(self, scope):
        return dict((kvp.key.python_value(scope), kvp.value.python_value(scope)) for kvp in self.values)

    def set_item(self, attr, value, scope):
        python_key = attr.python_value(scope)
        for kvp in self.values:
            if kvp.key.python_value(scope) == python_key:
                kvp.value = value
                return
        key = attr.get_value(scope)
        self.values.append(PlywoodKvp(key, value))

    def get_item(self, attr, scope):
        key = attr.python_value(scope)
        for kvp in self.values:
            if kvp.key.python_value(scope) == key:
                return kvp.value
        return None

    def set_attr(self, attr, value, scope):
        return self.set_item(PlywoodString(value.location, attr.get_name()), value, scope)

    def get_attr(self, attr, scope):
        key = attr.get_name()
        for kvp in self.values:
            if kvp.key.python_value(scope) == key:
                return kvp.value
        return None

    def __repr__(self):
        return type(self).__name__ + '{' + ', '.join(repr(v) for v in self.values) + '}'

    def __str__(self):
        return '{' + ', '.join(str(v) for v in self.values) + '}'


class PlywoodCallable(PlywoodValue):
    def __init__(self, fn):
        self.fn = fn
        super().__init__(location=None)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.fn)
        else:
            copy = instance
        return super().copy(copy)

    def run(self, states, scope):
        if not hasattr(self, 'location'):
            raise PlywoodRuntimeError(self.location, scope, repr(self) + ' has no location')
        arguments = PlywoodParens(self.location, [])
        block = PlywoodBlock(self.location, [])
        if Continue() in states:
            return self.call(states, scope, arguments, block)
        else:
            return None

    def python_value(self, scope):
        return self.get_value(scope).python_value(scope)

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

        self.accepts_states = accepted_states
        self.suppress_newline = suppress_newline
        super().__init__(fn)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.fn, self.accepts_states, self.suppress_newline)
        else:
            copy = instance
        return super().copy(copy)

    def call(self, states, scope, arguments, block):
        if any(state in states for state in self.accepts_states):
            states, retval = self.fn(states, scope, arguments, block)
            if self.suppress_newline:
                states.append(SuppressOneNewline())
            return PlywoodWrapper(self.location, [states, retval])
        states.append(SuppressOneNewline())
        return states, PlywoodWrapper(self.location, '')


class PlywoodHtmlPlugin(PlywoodCallable):
    def __init__(self, fn):
        self.classes = []
        self.id_name = None
        super().__init__(fn)

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.fn)
        else:
            copy = instance
        copy.id_name = self.id_name
        copy.classes.extend(self.classes)
        return super().copy(copy)

    def call(self, states, scope, arguments, block):
        return [Continue()], PlywoodWrapper(self.location, self.fn(scope, arguments, block, self.classes, id_name=self.id_name))

    def get_attr(self, attr, scope):
        copy = self.copy()
        copy.classes.append(attr.get_name())
        return copy

    def assign_id(self, attr, scope):
        copy = self.copy()
        copy.id_name = attr.get_name()
        return copy


class PlywoodFunction(PlywoodCallable):
    def __init__(self, fn, accepts_block=False):
        self.fn = fn
        self.accepts_block = accepts_block

    def copy(self, instance=None):
        if instance is None:
            copy = type(self)(self.fn, self.accepts_block)
        else:
            copy = instance
        return super().copy(copy)

    def call(self, states, scope, arguments, block):
        args = list(arg.python_value(scope) for arg in arguments.args)
        kwargs = dict(
            (item.key.python_value(scope), item.value.python_value(scope))
                for item in arguments.kwargs
                )
        if self.accepts_block:
            def inside(indent=False):
                if indent:
                    return scope['__env'].indent(block.python_value(scope))
                return block.python_value(scope)
            retval = self.fn(inside, *args, **kwargs)
        else:
            try:
                retval = self.fn(*args, **kwargs)
            except TypeError as e:
                raise PlywoodRuntimeError(self.location, scope, "{self!r} raised {e!r}".format(self=self, e=e))
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
    if isinstance(value, str):
        return PlywoodString(location, value)
    if isinstance(value, int) or isinstance(value, float):
        return PlywoodNumber(location, value)
    if callable(value):
        retval = PlywoodFunction(value)
        retval.location = location
        return retval
    return PlywoodPythonValue(location, value)
