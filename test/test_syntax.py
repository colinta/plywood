from pytest import raises
from chomsky import ParseException
from plywood import (
    Plywood, PlywoodValue,
    PlywoodVariable, PlywoodString, PlywoodNumber,
    PlywoodOperator, PlywoodUnaryOperator,
    PlywoodParens, PlywoodList, PlywoodDict,
    PlywoodKvp, PlywoodFunction, PlywoodBlock,
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
    assert isinstance(test, PlywoodFunction)
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


def assert_parens(test, arg_count=None, kwarg_count=0):
    assert isinstance(test, PlywoodParens)
    if arg_count is not None:
        assert len(test.args) == arg_count
        assert len(test.kwargs) == kwarg_count


def assert_dict(test, count=None):
    assert isinstance(test, PlywoodDict)
    if count is not None:
        assert len(test.values) == count


def test_variable():
    test = Plywood('foo').parse()[0]
    assert_variable(test, 'foo')


def test_variable_dashes():
    test = Plywood('foo-bar').parse()[0]
    assert_variable(test, 'foo-bar')


def test_variable_colons():
    test = Plywood('foo:bar').parse()[0]
    assert_variable(test, 'foo:bar')


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
    assert_parens(test, 1)

    assert_operator(test.args[0], '+')
    assert_unary(test.args[0].left, '-')
    assert_variable(test.args[0].left.value, 'foo')
    assert_unary(test.args[0].right, '~')
    assert_variable(test.args[0].right.value, 'bar')


def test_parens_two():
    test = Plywood('(a, b)').parse()[0]
    assert_parens(test, 2)

    assert_variable(test.args[0], 'a')
    assert_variable(test.args[1], 'b')


def test_args_two():
    test = Plywood('foo a, b').parse()[0]
    assert_function(test, 'foo')


def test_args_three():
    test = Plywood('foo a, b, c').parse()[0]
    assert_function(test, 'foo')

    assert_variable(test.right.args[0], 'a')
    assert_variable(test.right.args[1], 'b')
    assert_variable(test.right.args[2], 'c')


def test_args_three_kwarg():
    test = Plywood('foo a, b, d=e, c, f=g').parse()[0]
    assert_function(test, 'foo')

    assert_parens(test.right, 3, 2)
    assert_variable(test.right.args[0], 'a')
    assert_variable(test.right.args[1], 'b')
    assert_variable(test.right.args[2], 'c')
    assert_kvp(test.right.kwargs[0], 'd')
    assert_variable(test.right.kwargs[0].value, 'e')
    assert_kvp(test.right.kwargs[1], 'f')
    assert_variable(test.right.kwargs[1].value, 'g')


def test_parens_multiline():
    test = Plywood('''(
    a,
    b,
    c,
)''').parse()[0]
    assert_parens(test, 3)

    assert_variable(test.args[0], 'a')
    assert_variable(test.args[1], 'b')
    assert_variable(test.args[2], 'c')


def test_parens_args():
    test = Plywood('''(
    a,
    b,
    c=d,
)''').parse()[0]
    assert_parens(test, 2, 1)

    assert_variable(test.args[0], 'a')
    assert_variable(test.args[1], 'b')
    assert_kvp(test.kwargs[0], 'c')
    assert_variable(test.kwargs[0].value, 'd')


def test_list():
    test = Plywood('[1, "two", three, (four) + -five]').parse()[0]
    assert isinstance(test, PlywoodList)

    assert_number(test.values[0], 1)
    assert_string(test.values[1], 'two')
    assert_variable(test.values[2], 'three')
    assert_operator(test.values[3], '+')
    assert isinstance(test.values[3].left, PlywoodParens)
    assert_variable(test.values[3].left.args[0], 'four')
    assert_unary(test.values[3].right, '-')
    assert_variable(test.values[3].right.value, 'five')


def test_assign():
    test = Plywood('a = b = c + 1').parse()[0]

    assert_operator(test, '=')
    assert_variable(test.left, 'a')
    assert_operator(test.right, '=')
    assert_variable(test.right.left, 'b')
    assert_operator(test.right.right, '+')
    assert_variable(test.right.right.left, 'c')
    assert_number(test.right.right.right, 1)


def test_function():
    test = Plywood('foo(bar, baz)').parse()[0]
    assert_function(test, 'foo')
    assert_parens(test.right, 2)

    assert_variable(test.right.args[0], 'bar')
    assert_variable(test.right.args[1], 'baz')


def test_function_kwargs():
    test = Plywood('foo(bar, 1, key="value")').parse()[0]
    assert_function(test, 'foo')
    assert_variable(test.left, 'foo')
    assert_parens(test.right, 2, 1)
    assert_variable(test.right.args[0], 'bar')
    assert_number(test.right.args[1], 1)
    assert_kvp(test.right.kwargs[0], 'key')
    assert_string(test.right.kwargs[0].value, 'value')


def test_autofunction():
    test = Plywood('foo bar, baz(a b), c=d').parse()[0]
    assert_function(test, 'foo')

    assert_variable(test.right.args[0], 'bar')
    assert_operator(test.right.args[1], '()')
    assert_kvp(test.right.kwargs[0], 'c')
    assert_variable(test.right.kwargs[0].value, 'd')


def test_dict():
    test = Plywood('{"foo": bar}').parse()[0]
    assert_dict(test, 1)
    assert_kvp(test.values[0], 'foo')
    assert_variable(test.values[0].value, 'bar')


def test_dict_two():
    test = Plywood('{"foo": bar, bar: baz}').parse()[0]
    assert_dict(test, 2)
    assert_kvp(test.values[0], 'foo')
    assert_variable(test.values[0].value, 'bar')
    assert_kvp(test.values[1], PlywoodVariable('bar'))
    assert_variable(test.values[1].value, 'baz')


def test_dict_multiline():
    test = Plywood('''{
        "foo": bar,
        "bar": baz
        }''').parse()[0]
    assert_dict(test, 2)
    assert_kvp(test.values[0], 'foo')
    assert_variable(test.values[0].value, 'bar')
    assert_kvp(test.values[1], PlywoodVariable('bar'))
    assert_variable(test.values[1].value, 'baz')


def test_multiline_commands():
    test = Plywood("foo\nbar").parse()
    assert_variable(test[0], 'foo')
    assert_variable(test[1], 'bar')


def test_lots_of_multiline_commands():
    test = Plywood("""
foo
"foo"
1
123
bar
foo(bar, item='value')
""").parse()
    assert_variable(test[0], 'foo')
    assert_string(test[1], 'foo')
    assert_number(test[2], 1)
    assert_number(test[3], 123)
    assert_variable(test[4], 'bar')
    assert_operator(test[5], '()')


def test_block_indent_fail():
    with raises(ParseException):
        test = Plywood('   foo').parse()
        assert test == None


def test_block():
    test = Plywood('''
if True or False:
    print "True!"
''').parse()

    assert_block(test, 1)
    assert_function(test[0], 'if')
    assert_block(test[0].block, 1)
    assert_function(test[0].block.lines[0], 'print')
    assert_parens(test[0].block.lines[0].right, 1)
    assert_string(test[0].block.lines[0].right[0], 'True!')
    assert_parens(test[0].right, 1)
    assert_operator(test[0].right[0], 'or')
    assert_variable(test[0].right[0].left, 'True')
    assert_variable(test[0].right[0].right, 'False')


def test_inline_block():
    """
    same as test_block, but inline block.
    """
    test = Plywood('''
if True or False:  print "True!"
''').parse()

    assert_block(test, 1)
    assert_function(test[0], 'if')
    assert_block(test[0].block, 1)
    assert_function(test[0].block.lines[0], 'print')
    assert_parens(test[0].block.lines[0].right, 1)
    assert_string(test[0].block.lines[0].right[0], 'True!')
    assert_parens(test[0].right, 1)
    assert_operator(test[0].right[0], 'or')
    assert_variable(test[0].right[0].left, 'True')
    assert_variable(test[0].right[0].right, 'False')


def test_happy_fun_block():
    test = Plywood('''
div: p: 'text'
''').parse()

    assert_block(test, 1)
    assert_function(test[0], 'div')
    assert_block(test[0].block, 1)
    assert_function(test[0].block[0], 'p')
    assert_block(test[0].block[0].block, 1)
    assert_string(test[0].block[0].block[0], 'text')


def test_classy_div():
    test = Plywood('''
div.classy: 'text'
''').parse()

    assert_block(test, 1)
    assert_function(test[0])
    assert_operator(test[0].left, '.')
    assert_variable(test[0].left.left, 'div')
    assert_variable(test[0].left.right, 'classy')
    assert_block(test[0].block, 1)
    assert_string(test[0].block[0], 'text')


def test_id_div():
    test = Plywood('''
div@any_id: 'text'
''').parse()

    assert_block(test, 1)
    assert_function(test[0])
    assert_operator(test[0].left, '@')
    assert_variable(test[0].left.left, 'div')
    assert_variable(test[0].left.right, 'any_id')
    assert_block(test[0].block, 1)
    assert_string(test[0].block[0], 'text')


def test_classy_id_div():
    test = Plywood('''
div.classy@any_id: 'text'
''').parse()

    assert_block(test, 1)
    assert_function(test[0])
    assert_operator(test[0].left, '@')
    assert_operator(test[0].left.left, '.')
    assert_variable(test[0].left.left.left, 'div')
    assert_variable(test[0].left.left.right, 'classy')
    assert_variable(test[0].left.right, 'any_id')
    assert_block(test[0].block, 1)
    assert_string(test[0].block[0], 'text')


def test_multi_inline():
    test = Plywood('''
foo: bar
foo: bar
''').parse()
    assert_block(test, 2)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 1)
    assert_variable(test[0].block[0], 'bar')
    assert_function(test[1], 'foo')
    assert_block(test[1].block, 1)
    assert_variable(test[0].block[0], 'bar')


def test_empty_blocks():
    test = Plywood('''
foo:
foo:
foo:
foo:
''').parse()
    assert_block(test, 4)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 0)
    assert_function(test[1], 'foo')
    assert_block(test[1].block, 0)
    assert_function(test[2], 'foo')
    assert_block(test[2].block, 0)
    assert_function(test[3], 'foo')
    assert_block(test[3].block, 0)


def test_multi_block():
    test = Plywood('''
foo:
    foo:
        foo:
            foo:
''').parse()
    assert_block(test, 1)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 1)
    assert_function(test[0].block[0], 'foo')
    assert_block(test[0].block[0].block, 1)
    assert_function(test[0].block[0].block[0], 'foo')
    assert_block(test[0].block[0].block[0].block, 1)
    assert_function(test[0].block[0].block[0].block[0], 'foo')
    assert_block(test[0].block[0].block[0].block[0].block, 0)


def test_multi_mixed():
    test = Plywood('''
foo:
    foo:
        BAH:  bar
        foo:  bar
''').parse()
    assert_block(test, 1)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 1)
    assert_function(test[0].block[0], 'foo')
    assert_block(test[0].block[0].block, 2)
    assert_function(test[0].block[0].block[0], 'BAH')
    assert_block(test[0].block[0].block[0].block, 1)
    assert_variable(test[0].block[0].block[0].block[0], 'bar')
    assert_function(test[0].block[0].block[1], 'foo')
    assert_block(test[0].block[0].block[1].block, 1)
    assert_variable(test[0].block[0].block[1].block[0], 'bar')


def test_multi_mixed_fail():
    with raises(ParseException):
        Plywood('''
foo:
    foo:
        BAH:  bar
        # too much indent:
          foo:  bar
''').parse()
        assert False


def test_multi_block_in_out():
    test = Plywood('''
foo:
    foo
BAH:
    BAH
''').parse()
    assert_block(test, 2)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 1)
    assert_variable(test[0].block[0], 'foo')
    assert_function(test[1], 'BAH')
    assert_block(test[1].block, 1)
    assert_variable(test[1].block[0], 'BAH')


def test_multi_mixed_block_in_out():
    test = Plywood('''
foo:
    foo
BAH: BAH
bar:
    baz
baz: 'baz'
''').parse()
    assert_block(test, 4)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 1)
    assert_variable(test[0].block[0], 'foo')

    assert_function(test[1], 'BAH')
    assert_block(test[1].block, 1)
    assert_variable(test[1].block[0], 'BAH')

    assert_function(test[2], 'bar')
    assert_block(test[2].block, 1)
    assert_variable(test[2].block[0], 'baz')

    assert_function(test[3], 'baz')
    assert_block(test[3].block, 1)
    assert_string(test[3].block[0], 'baz')
