from __future__ import division
from plywood import (
    PlywoodOperator, PlywoodUnaryOperator, PlywoodVariable,
    PlywoodParens, PlywoodBlock, PlywoodCallOperator,
    )
from plywood.runtime import Skip
from plywood.runtime import Continue


@PlywoodOperator.register('+')
def plus(left, right, scope):
    left = left.python_value(scope)
    right = right.python_value(scope)
    if isinstance(left, basestring):
        return left + (right and right or '')
    return left + right


@PlywoodOperator.register('-')
def minus(left, right, scope):
    return left.python_value(scope) - right.python_value(scope)


@PlywoodOperator.register('*')
def times(left, right, scope):
    return left.python_value(scope) * right.python_value(scope)


@PlywoodOperator.register('**')
def power(left, right, scope):
    return left.python_value(scope) ** right.python_value(scope)


@PlywoodOperator.register('/')
def divide(left, right, scope):
    return left.python_value(scope) / right.python_value(scope)


@PlywoodOperator.register('//')
def int_divide(left, right, scope):
    return left.python_value(scope) // right.python_value(scope)


@PlywoodOperator.register('==')
def equals(left, right, scope):
    return left.python_value(scope) == right.python_value(scope)


@PlywoodOperator.register('!=')
def not_equals(left, right, scope):
    return left.python_value(scope) != right.python_value(scope)


@PlywoodOperator.register('<=')
def less_than_or_equal(left, right, scope):
    return left.python_value(scope) <= right.python_value(scope)


@PlywoodOperator.register('<')
def less_than(left, right, scope):
    return left.python_value(scope) < right.python_value(scope)


@PlywoodOperator.register('>')
def greater_than(left, right, scope):
    return left.python_value(scope) > right.python_value(scope)


@PlywoodOperator.register('>=')
def greater_than_or_equal(left, right, scope):
    return left.python_value(scope) >= right.python_value(scope)


@PlywoodOperator.register('in')
def boolean_in(left, right, scope):
    left = left.python_value(scope)
    right = right.python_value(scope)
    return left in right


@PlywoodOperator.register('is')
def boolean_is(left, right, scope):
    return left.python_value(scope) is right.python_value(scope)


@PlywoodOperator.register('and')
def boolean_and(left, right, scope):
    return left.python_value(scope) and right.python_value(scope)


@PlywoodOperator.register('or')
def boolean_or(left, right, scope):
    return left.python_value(scope) or right.python_value(scope)


# 'test' | date => date('test')
# '<test>' | escape | json  # => json(escape('<test>'))
@PlywoodOperator.register('|')
def binary_or(left, right, scope):
    if isinstance(right, PlywoodCallOperator):
        right.right.args.insert(0, left.get_value(scope))
        arguments = right.right
        _, retval = right.run([Continue()], scope)
    else:
        arguments = PlywoodParens(right.location, [left])
        block = PlywoodBlock(right.location, [])
        _, retval = right.call([Continue()], scope, arguments, block)
    return retval


@PlywoodOperator.register('%')
def modulo(left, right, scope):
    return left.python_value(scope) % right.python_value(scope)


def item_setter(self, right, value, scope):
    self.left.get_value(scope).set_item(self.right, value, scope)


@PlywoodOperator.register('[]', setter=item_setter)
def get_item(left, right, scope):
    return left.get_item(right, scope)


def attr_setter(self, right, value, scope):
    self.left.get_value(scope).set_attr(self.right, value, scope)


@PlywoodOperator.register('.', setter=attr_setter)
def get_attr(left, right, scope):
    return left.get_attr(right, scope)


@PlywoodUnaryOperator.register('.')
def unary_get_attr(value, scope):
    return PlywoodOperator.handle('.', PlywoodVariable(value.location, 'div'), value, scope)


@PlywoodUnaryOperator.register('-')
def negate(value, scope):
    return - value.python_value(scope)


@PlywoodUnaryOperator.register('not')
def not_(value, scope):
    return not value.python_value(scope)


@PlywoodOperator.register('=', state=Skip())
def assign(left, right, scope):
    left.set_attr(right, right.get_value(scope), scope)
    return right


@PlywoodOperator.register('+=', state=Skip())
def plus_assign(left, right, scope):
    value = PlywoodOperator.handle('+', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('-=', state=Skip())
def minus_assign(left, right, scope):
    value = PlywoodOperator.handle('-', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('*=', state=Skip())
def times_assign(left, right, scope):
    value = PlywoodOperator.handle('*', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('**=', state=Skip())
def power_assign(left, right, scope):
    value = PlywoodOperator.handle('**', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('/=', state=Skip())
def divide_assign(left, right, scope):
    value = PlywoodOperator.handle('/', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('//=', state=Skip())
def int_divide_assign(left, right, scope):
    value = PlywoodOperator.handle('//', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('%=', state=Skip())
def modulo_assign(left, right, scope):
    value = PlywoodOperator.handle('%', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('or=', state=Skip())
def boolean_or_assign(left, right, scope):
    value = PlywoodOperator.handle('or', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)


@PlywoodOperator.register('and=', state=Skip())
def boolean_and_assign(left, right, scope):
    value = PlywoodOperator.handle('and', left, right, scope)
    return PlywoodOperator.handle('=', left, value, scope)
