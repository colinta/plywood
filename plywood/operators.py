from __future__ import division
from plywood import (
    PlywoodOperator, PlywoodUnaryOperator, PlywoodVariable,
    PlywoodSlice, PlywoodIndices,
    )


@PlywoodOperator.register('+')
def plus(left, right, scope):
    return left.python_value(scope) + right.python_value(scope)


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


@PlywoodOperator.register('<')
def greater_than(left, right, scope):
    return left.python_value(scope) < right.python_value(scope)


@PlywoodOperator.register('>=')
def greater_than_or_equal(left, right, scope):
    return left.python_value(scope) >= right.python_value(scope)


@PlywoodOperator.register('in')
def boolean_in(left, right, scope):
    return left.python_value(scope) in right.python_value(scope)


@PlywoodOperator.register('is')
def boolean_is(left, right, scope):
    return left.python_value(scope) is right.python_value(scope)


@PlywoodOperator.register('and')
def boolean_and(left, right, scope):
    return left.python_value(scope) and right.python_value(scope)


@PlywoodOperator.register('or')
def boolean_or(left, right, scope):
    return left.python_value(scope) or right.python_value(scope)


@PlywoodOperator.register('&')
def binary_and(left, right, scope):
    return left.python_value(scope) & right.python_value(scope)


@PlywoodOperator.register('|')
def binary_or(left, right, scope):
    return left.python_value(scope) | right.python_value(scope)


@PlywoodOperator.register('<<')
def bitshift_left(left, right, scope):
    return left.python_value(scope) << right.python_value(scope)


@PlywoodOperator.register('>>')
def bitshift_right(left, right, scope):
    return left.python_value(scope) >> right.python_value(scope)


@PlywoodOperator.register('%')
def modulo(left, right, scope):
    return left.python_value(scope) % right.python_value(scope)


@PlywoodOperator.register('[]')
def get_item(left, right, scope):
    return left.get_item(scope, right)


@PlywoodOperator.register('.')
def get_attr(left, right, scope):
    return left.get_attr(scope, right)


@PlywoodUnaryOperator.register('.')
def unary_get_attr(value, scope):
    return PlywoodOperator.handle('.', PlywoodVariable(value.location, 'div'), value, scope)


@PlywoodOperator.register('@')
def set_id(left, right, scope):
    return left.set_id(scope, right)


@PlywoodUnaryOperator.register('@')
def unary_set_id(value, scope):
    return PlywoodOperator.handle('@', PlywoodVariable(value.location, 'div'), value, scope)


@PlywoodUnaryOperator.register('-')
def negate(value, scope):
    return - value.python_value(scope)


@PlywoodUnaryOperator.register('~')
def invert(value, scope):
    return ~ value.python_value(scope)


@PlywoodUnaryOperator.register('not')
def not_(value, scope):
    return not value.python_value(scope)


@PlywoodOperator.register('=')
def assign(left, right, scope):
    left = left.get_value(scope)
    scope[left.get_name()] = right
    return right


@PlywoodOperator.register('+=')
def plus_assign(left, right, scope):
    value = PlywoodOperator.handle('+', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('-=')
def minus_assign(left, right, scope):
    value = PlywoodOperator.handle('-', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('*=')
def times_assign(left, right, scope):
    value = PlywoodOperator.handle('*', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('**=')
def power_assign(left, right, scope):
    value = PlywoodOperator.handle('**', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('/=')
def divide_assign(left, right, scope):
    value = PlywoodOperator.handle('/', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('//=')
def int_divide_assign(left, right, scope):
    value = PlywoodOperator.handle('//', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('%=')
def modulo_assign(left, right, scope):
    value = PlywoodOperator.handle('%', left, right, scope)
    PlywoodOperator.handle('=', left, value, scope)
    return right


@PlywoodOperator.register('.=')
def call_assign(left, right, scope):
    left = left.get_value(scope)
    left = scope[left.get_name()].get_attr(right)
    PlywoodOperator.handle('=', left, right, scope)
    return right
