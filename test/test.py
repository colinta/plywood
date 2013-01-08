from plywood import (
    Plywood, PlywoodVariable, PlywoodString, PlywoodNumber,
    PlywoodOperator, PlywoodUnaryOperator
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


def test_variable():
    test = Plywood('foo').parse()[0]
    assert_variable(test, 'foo')


def test_blank():
    assert [] == Plywood('# comment').parse()
    assert [] == Plywood('\n\n# comment\n\n').parse()
    assert [] == Plywood('\n\n# comment\n # \n').parse()
    assert [] == Plywood('\n\n# comment\n # \n#').parse()
    assert [] == Plywood('\n\n# comment\n   \n#').parse()


def test_comment_with_variable():
    test = Plywood('foo # comment').parse()[0]
    assert_variable(test, 'foo')

    test = Plywood('foo # comment\nbar # comment').parse()[0]
    assert_variable(test, 'foo')

    test = Plywood('\n# comment1\nfoo # comment2\n\n\n  # comment3').parse()[0]
    assert_variable(test, 'foo')


def test_string():
    test = Plywood('"foo"').parse()[0]
    assert_string(test, 'foo')


def test_integer():
    test = Plywood('1').parse()[0]
    assert_number(test, 1)


def test_neg_integer():
    test = Plywood('-1').parse()[0]
    assert_number(test, -1)


def test_float():
    test = Plywood('0.123').parse()[0]
    assert_number(test, 0.123)

    test = Plywood('1.123').parse()[0]
    assert_number(test, 1.123)


def test_neg_float():
    test = Plywood('-0.123').parse()[0]
    assert_number(test, -0.123)


def test_hexadecimal():
    test = Plywood('0x1e32').parse()[0]
    assert_number(test, 7730)

    test = Plywood('0x0001ea').parse()[0]
    assert_number(test, 490)

    test = Plywood('0x0').parse()[0]
    assert_number(test, 0)

    test = Plywood('0xFFFF').parse()[0]
    assert_number(test, 65535)


def test_octal():
    test = Plywood('0o716').parse()[0]
    assert_number(test, 462)

    test = Plywood('0o0716').parse()[0]
    assert_number(test, 462)


def test_binary():
    test = Plywood('0b010101').parse()[0]
    assert_number(test, 21)


def test_neg_hexadecimal():
    test = Plywood('-0x1e32').parse()[0]
    assert_number(test, -7730)


def test_unary():
    test = Plywood('-bar').parse()[0]
    assert_unary(test, '-')
    assert_variable(test.value, 'bar')


def test_addition():
    test = Plywood('foo + bar').parse()[0]
    assert_operator(test, '+')
    assert_variable(test.left, 'foo')
    assert_variable(test.right, 'bar')


def test_multiplication():
    test = Plywood('foo * bar').parse()[0]
    assert_operator(test, '*')
    assert_variable(test.left, 'foo')
    assert_variable(test.right, 'bar')


def test_add_mult_precedence():
    test = Plywood('foo + bar * baz').parse()[0]
    assert_operator(test, '+')
    assert_variable(test.left, 'foo')
    assert_operator(test.right, '*')
    assert_variable(test.right.left, 'bar')
    assert_variable(test.right.right, 'baz')

    test = Plywood('foo * bar + baz').parse()[0]
    assert_operator(test, '+')
    assert_variable(test.right, 'baz')
    assert_operator(test.left, '*')
    assert_variable(test.left.left, 'foo')
    assert_variable(test.left.right, 'bar')

    test = Plywood('foo + bar + baz').parse()[0]
    assert_operator(test, '+')
    assert_variable(test.right, 'baz')
    assert_operator(test.left, '+')
    assert_variable(test.left.left, 'foo')
    assert_variable(test.left.right, 'bar')

    test = Plywood('foo * bar + baz * foo').parse()[0]
    assert_operator(test, '+')
    assert_operator(test.left, '*')
    assert_variable(test.left.left, 'foo')
    assert_variable(test.left.right, 'bar')
    assert_operator(test.right, '*')
    assert_variable(test.right.left, 'baz')
    assert_variable(test.right.right, 'foo')


def test_unary_precedence():
    test = Plywood('-~bar').parse()[0]
    assert_unary(test, '-')
    assert_unary(test.value, '~')
    assert_variable(test.value.value, 'bar')


def test_precedence():
    test = Plywood('1 < 2 and 2 > 1 and 2+2 == 4').parse()[0]
    assert_operator(test, 'and')
    assert_operator(test.left, 'and')
    assert_operator(test.left.left, '<')
    assert_number(test.left.left.left, 1)
    assert_number(test.left.left.right, 2)
    assert_operator(test.right, '==')
    assert_operator(test.right.left, '+')
    assert_number(test.right.left.left, 2)
    assert_number(test.right.left.right, 2)
    assert_number(test.right.right, 4)

    test = Plywood('2*3**4').parse()[0]
    assert_operator(test, '*')
    assert_number(test.left, 2)
    assert_operator(test.right, '**')
    assert_number(test.right.left, 3)
    assert_number(test.right.right, 4)

    test = Plywood('2**3*4').parse()[0]
    assert_operator(test, '*')
    assert_operator(test.left, '**')
    assert_number(test.left.left, 2)
    assert_number(test.left.right, 3)
    assert_number(test.right, 4)

    test = Plywood('2**3**4').parse()[0]
    assert_operator(test, '**')
    assert_number(test.left, 2)
    assert_operator(test.right, '**')
    assert_number(test.right.left, 3)
    assert_number(test.right.right, 4)

    test = Plywood('-foo + ~bar').parse()[0]
    assert_operator(test, '+')
    assert_unary(test.left, '-')
    assert_variable(test.left.value, 'foo')
    assert_unary(test.right, '~')
    assert_variable(test.right.value, 'bar')


def test_parens():
    test = Plywood('(-foo + ~bar)').parse()[0]
    assert_operator(test, '+')
    assert_unary(test.left, '-')
    assert_variable(test.left.value, 'foo')
    assert_unary(test.right, '~')
    assert_variable(test.right.value, 'bar')

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
