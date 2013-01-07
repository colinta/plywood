from plywood import (
    Plywood, PlywoodVariable, PlywoodString, PlywoodNumber, PlywoodOperator
    )


def test_variable():
    assert Plywood('foo').parse() == [[PlywoodVariable('foo')]]


def test_string():
    assert Plywood('"foo"').parse() == [[PlywoodString('"foo"')]]


def test_integer():
    assert Plywood('1').parse() == [[PlywoodNumber('1')]]


def test_neg_integer():
    assert Plywood('-1').parse() == [[PlywoodNumber('-1')]]


def test_float():
    assert Plywood('0.123').parse() == [[PlywoodNumber('0.123')]]
    assert Plywood('1.123').parse() == [[PlywoodNumber('1.123')]]


def test_neg_float():
    assert Plywood('-0.123').parse() == [[PlywoodNumber('-0.123')]]


def test_hexadecimal():
    assert Plywood('0x1e32').parse() == [[PlywoodNumber('0x1e32')]]
    assert Plywood('0x0001ea').parse() == [[PlywoodNumber('0x0001ea')]]
    assert Plywood('0x0').parse() == [[PlywoodNumber('0x0')]]
    assert Plywood('0xFFFF').parse() == [[PlywoodNumber('0xFFFF')]]


def test_octal():
    assert Plywood('0o716').parse() == [[PlywoodNumber('0o716')]]
    assert Plywood('0o0716').parse() == [[PlywoodNumber('0o0716')]]


def test_binary():
    assert Plywood('0b010101').parse() == [[PlywoodNumber('0b010101')]]


def test_neg_hexadecimal():
    assert Plywood('-0x1e32').parse() == [[PlywoodNumber('-0x1e32')]]


def test_addition():
    assert Plywood('foo + bar').parse() == [
        [PlywoodVariable('foo'), PlywoodOperator('+'), PlywoodVariable('bar')]
    ]

# print repr(Plywood('foo + bar').parse())
# print repr(Plywood('foo - bar').parse())
# print repr(Plywood('foo * bar').parse())
# print repr(Plywood('foo / bar').parse())
# print repr(Plywood('foo * bar').parse())
# print repr(Plywood('foo % bar').parse())
# print repr(Plywood('foo / bar').parse())
# print repr(Plywood('foo . bar').parse())
# print repr(Plywood('foo = bar = foo + 1').parse())
# print repr(Plywood('foo(bar)').parse())
# print repr(Plywood('foo(bar, 1, key="value")').parse())
# print repr(Plywood('{foo: bar}').parse())
# print repr(Plywood('{"foo": "bar"}').parse())
# print repr(Plywood("foo\nbar").parse())
# print repr(Plywood("""
# foo
# "foo"
# 1
# 123
# bar
# foo(bar, item='value')
# """).parse())
