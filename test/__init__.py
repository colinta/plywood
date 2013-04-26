from plywood import plywood
from plywood import (
    PlywoodValue,
    PlywoodVariable, PlywoodString, PlywoodNumber,
    PlywoodOperator, PlywoodUnaryOperator,
    PlywoodParens, PlywoodList, PlywoodIndices, PlywoodDict,
    PlywoodKvp, PlywoodCallOperator, PlywoodBlock,
    )


def assert_number(test, value):
    assert isinstance(test, PlywoodNumber)
    assert isinstance(test.value, type(value))
    assert test.value == value


def assert_string(test, value):
    assert isinstance(test, PlywoodString)
    assert test.value == value


def assert_variable(test, name):
    assert isinstance(test, PlywoodVariable)
    assert test.name == name


def assert_unary(test, op):
    assert isinstance(test, PlywoodUnaryOperator)
    assert test.operator == op


def assert_operator(test, op):
    assert isinstance(test, PlywoodOperator)
    assert test.operator == op


def assert_function(test, name=None):
    assert isinstance(test, PlywoodCallOperator)
    if name:
        assert_variable(test.left, name)


def assert_kvp(test, key):
    assert isinstance(test, PlywoodKvp)
    if key:
        if not isinstance(key, PlywoodValue):
            assert_string(test.key, key)
        else:
            assert test.key == key


def assert_block(test, count=None):
    assert isinstance(test, PlywoodBlock)
    if count is not None:
        assert len(test.lines) == count


def assert_list(test, value_count=None):
    assert isinstance(test, PlywoodList)
    assert len(test.values) == value_count


def assert_indices(test, value_count=None):
    assert isinstance(test, PlywoodIndices)
    assert len(test.values) == value_count


def assert_parens(test, arg_count=None, kwarg_count=0):
    assert isinstance(test, PlywoodParens)
    if arg_count is not None:
        assert len(test.args) == arg_count
        assert len(test.kwargs) == kwarg_count


def assert_dict(test, count=None):
    assert isinstance(test, PlywoodDict)
    if count is not None:
        assert len(test.values) == count


def assert_output(input, desired, scope={}, **options):
    actual = plywood(input, scope, **options)
    assert_strings(actual, desired)


def assert_strings(actual, desired):
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual
