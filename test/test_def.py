from pytest import raises
from plywood.exceptions import InvalidArguments
from . import assert_output


def test_def_fail_empty():
    input = '''
def foo():
foo
'''
    with raises(InvalidArguments):
        assert_output(input, '')


def test_def():
    input = '''
def foo():
    'foo'
foo        # there was a bug where this line output an extra newline
foo()      # but this didn't.
'''
    desired = '''foo
foo
'''
    assert_output(input, desired)


def test_def_arg():
    input = '''
def foo(bar):
    'foo' + bar + 'foo'
foo('baz')
'''
    desired = '''foobazfoo
'''
    assert_output(input, desired)


def test_def_arg_fail_toomany():
    input = '''
def foo(bar):
    'foo' + bar + 'foo'
foo('baz', 'baz')
'''
    with raises(InvalidArguments):
        assert_output(input, '')


def test_def_arg_fail_notenough():
    input = '''
def foo(bar):
    'foo' + bar + 'foo'
foo()
'''
    with raises(InvalidArguments):
        assert_output(input, '')


def test_def_kwarg():
    input = '''
def foo(bar):
    'foo' + bar + 'foo'
foo(bar='baz')
'''
    desired = '''foobazfoo
'''
    assert_output(input, desired)


def test_def_kwarg_fail_unknown_kwarg():
    input = '''
def foo(bar):
    'foo' + bar + 'foo'
foo(quux='baz')
'''
    with raises(InvalidArguments):
        assert_output(input, '')


def test_def_defaults():
    input = '''
def foo(bar='BAR'):
    'foo' + bar + 'foo'
foo()
foo('bar')
'''
    desired = '''fooBARfoo
foobarfoo
'''
    assert_output(input, desired)
