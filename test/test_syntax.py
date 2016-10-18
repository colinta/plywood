from pytest import raises
from chomsky import ParseException
from plywood import (
    plywood, Plywood, PlywoodVariable,
    )
from . import (
    assert_number,
    assert_string,
    assert_variable,
    assert_unary,
    assert_operator,
    assert_function,
    assert_kvp,
    assert_block,
    assert_list,
    assert_indices,
    assert_parens,
    assert_dict,
    )


def test_variable():
    test = Plywood('foo').compile()[0]
    assert_variable(test, 'foo')


def test_variable_dashes():
    test = Plywood('foo-bar').compile()[0]
    assert_variable(test, 'foo-bar')


def test_variable_colons():
    test = Plywood('foo:bar').compile()[0]
    assert_variable(test, 'foo:bar')


def test_blank():
    assert [] == Plywood('# comment').compile()
    assert [] == Plywood('\n\n# comment\n\n').compile()
    assert [] == Plywood('\n\n# comment\n # \n').compile()
    assert [] == Plywood('\n\n# comment\n # \n#').compile()
    assert [] == Plywood('\n\n# comment\n   \n#').compile()


def test_comment_with_variable():
    test = Plywood('foo # comment').compile()[0]
    assert_variable(test, 'foo')

    test = Plywood('foo # comment\nbar # comment').compile()[0]
    assert_variable(test, 'foo')

    test = Plywood('\n# comment1\nfoo # comment2\n\n\n  # comment3').compile()[0]
    assert_variable(test, 'foo')


def test_string_double():
    test = Plywood('"foo"').compile()[0]
    assert_string(test, 'foo')


def test_string_single():
    test = Plywood("'foo'").compile()[0]
    assert_string(test, 'foo')


def test_string_triple_double():
    test = Plywood('"""foo"""').compile()[0]
    assert_string(test, 'foo')


def test_string_triple_single():
    test = Plywood("'''foo'''").compile()[0]
    assert_string(test, 'foo')


def test_string_triple_double_multiline():
    test = Plywood('''"""
foo"""''').compile()[0]
    assert_string(test, 'foo')


def test_string_triple_double_multiline_w_lang():
    test = Plywood('''"""lang
foo"""''').compile()[0]
    assert_string(test, 'foo')


def test_string_triple_single_multiline():
    test = Plywood("""'''
foo'''""").compile()[0]
    assert_string(test, 'foo')


def test_string_triple_single_multiline_w_lang():
    test = Plywood("""'''lang
foo'''""").compile()[0]
    assert_string(test, 'foo')


def test_integer():
    test = Plywood('1').compile()[0]
    assert_number(test, 1)


def test_neg_integer():
    test = Plywood('-1').compile()[0]
    assert_number(test, -1)


def test_float():
    test = Plywood('0.123').compile()[0]
    assert_number(test, 0.123)

    test = Plywood('1.123').compile()[0]
    assert_number(test, 1.123)


def test_neg_float():
    test = Plywood('-0.123').compile()[0]
    assert_number(test, -0.123)


def test_hexadecimal():
    test = Plywood('0x1e32').compile()[0]
    assert_number(test, 7730)

    test = Plywood('0x0001ea').compile()[0]
    assert_number(test, 490)

    test = Plywood('0x0').compile()[0]
    assert_number(test, 0)

    test = Plywood('0xFFFF').compile()[0]
    assert_number(test, 65535)


def test_octal():
    test = Plywood('0o716').compile()[0]
    assert_number(test, 462)

    test = Plywood('0o0716').compile()[0]
    assert_number(test, 462)


def test_binary():
    test = Plywood('0b010101').compile()[0]
    assert_number(test, 21)


def test_neg_hexadecimal():
    test = Plywood('-0x1e32').compile()[0]
    assert_number(test, -7730)


def test_unary():
    test = Plywood('-bar').compile()[0]
    assert_unary(test, '-')
    assert_variable(test.value, 'bar')


def test_addition():
    test = Plywood('foo + bar').compile()[0]
    assert_operator(test, '+')
    assert_variable(test.left, 'foo')
    assert_variable(test.right, 'bar')


def test_multiplication():
    test = Plywood('foo * bar').compile()[0]
    assert_operator(test, '*')
    assert_variable(test.left, 'foo')
    assert_variable(test.right, 'bar')


def test_add_mult_precedence():
    test = Plywood('foo + bar * baz').compile()[0]
    assert_operator(test, '+')
    assert_variable(test.left, 'foo')
    assert_operator(test.right, '*')
    assert_variable(test.right.left, 'bar')
    assert_variable(test.right.right, 'baz')

    test = Plywood('foo * bar + baz').compile()[0]
    assert_operator(test, '+')
    assert_variable(test.right, 'baz')
    assert_operator(test.left, '*')
    assert_variable(test.left.left, 'foo')
    assert_variable(test.left.right, 'bar')

    test = Plywood('foo + bar + baz').compile()[0]
    assert_operator(test, '+')
    assert_variable(test.right, 'baz')
    assert_operator(test.left, '+')
    assert_variable(test.left.left, 'foo')
    assert_variable(test.left.right, 'bar')

    test = Plywood('foo * bar + baz * foo').compile()[0]
    assert_operator(test, '+')
    assert_operator(test.left, '*')
    assert_variable(test.left.left, 'foo')
    assert_variable(test.left.right, 'bar')
    assert_operator(test.right, '*')
    assert_variable(test.right.left, 'baz')
    assert_variable(test.right.right, 'foo')


def test_unary_precedence():
    test = Plywood('- not bar').compile()[0]
    assert_unary(test, '-')
    assert_unary(test.value, 'not')
    assert_variable(test.value.value, 'bar')


def test_pipe_precedence():
    test = Plywood('"str" + foo | fn("test") + "str"').compile()[0]
    assert_operator(test, '+')
    assert_string(test.right, 'str')
    assert_operator(test.left, '+')
    assert_string(test.left.left, 'str')
    assert_operator(test.left.right, '|')
    assert_variable(test.left.right.left, 'foo')
    assert_operator(test.left.right.right, '()')
    # assert_variable(test.left.right.right, 'fn')


def test_precedence():
    test = Plywood('1 < 2 and 2 > 1 and 2+2 == 4').compile()[0]
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

    test = Plywood('2*3**4').compile()[0]
    assert_operator(test, '*')
    assert_number(test.left, 2)
    assert_operator(test.right, '**')
    assert_number(test.right.left, 3)
    assert_number(test.right.right, 4)

    test = Plywood('2**3*4').compile()[0]
    assert_operator(test, '*')
    assert_operator(test.left, '**')
    assert_number(test.left.left, 2)
    assert_number(test.left.right, 3)
    assert_number(test.right, 4)

    test = Plywood('2**3**4').compile()[0]
    assert_operator(test, '**')
    assert_number(test.left, 2)
    assert_operator(test.right, '**')
    assert_number(test.right.left, 3)
    assert_number(test.right.right, 4)

    test = Plywood('-foo + - bar').compile()[0]
    assert_operator(test, '+')
    assert_unary(test.left, '-')
    assert_variable(test.left.value, 'foo')
    assert_unary(test.right, '-')
    assert_variable(test.right.value, 'bar')


def test_parens():
    test = Plywood('(-foo + -bar)').compile()[0]
    assert_parens(test, 1)

    assert_operator(test.args[0], '+')
    assert_unary(test.args[0].left, '-')
    assert_variable(test.args[0].left.value, 'foo')
    assert_unary(test.args[0].right, '-')
    assert_variable(test.args[0].right.value, 'bar')


def test_parens_two():
    test = Plywood('(a, b)').compile()[0]
    assert_parens(test, 2)

    assert_variable(test.args[0], 'a')
    assert_variable(test.args[1], 'b')


def test_args_two():
    test = Plywood('foo a, b').compile()[0]
    assert_function(test, 'foo')


def test_args_three():
    test = Plywood('foo a, b, c').compile()[0]
    assert_function(test, 'foo')

    assert_variable(test.right.args[0], 'a')
    assert_variable(test.right.args[1], 'b')
    assert_variable(test.right.args[2], 'c')


def test_args_three_kwarg():
    test = Plywood('foo a, b, d=e, c, f=g').compile()[0]
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
)''').compile()[0]
    assert_parens(test, 3)

    assert_variable(test.args[0], 'a')
    assert_variable(test.args[1], 'b')
    assert_variable(test.args[2], 'c')


def test_parens_args():
    test = Plywood('''(
    a,
    b,
    c=d,
)''').compile()[0]
    assert_parens(test, 2, 1)

    assert_variable(test.args[0], 'a')
    assert_variable(test.args[1], 'b')
    assert_kvp(test.kwargs[0], 'c')
    assert_variable(test.kwargs[0].value, 'd')


def test_list():
    test = Plywood('[1, "two", three, (four) + -five]').compile()[0]
    assert_list(test, 4)

    assert_number(test.values[0], 1)
    assert_string(test.values[1], 'two')
    assert_variable(test.values[2], 'three')
    assert_operator(test.values[3], '+')
    assert_parens(test.values[3].left, 1)
    assert_variable(test.values[3].left.args[0], 'four')
    assert_unary(test.values[3].right, '-')
    assert_variable(test.values[3].right.value, 'five')


def test_list_trailing_comma():
    test = Plywood('[1, 2, ]').compile()[0]
    assert_list(test, 2)
    assert_number(test.values[0], 1)
    assert_number(test.values[1], 2)


def test_assign():
    test = Plywood('a = b = c + 1').compile()[0]

    assert_operator(test, '=')
    assert_variable(test.left, 'a')
    assert_operator(test.right, '=')
    assert_variable(test.right.left, 'b')
    assert_operator(test.right.right, '+')
    assert_variable(test.right.right.left, 'c')
    assert_number(test.right.right.right, 1)


def test_function():
    test = Plywood('foo(bar, baz)').compile()[0]
    assert_function(test, 'foo')
    assert_parens(test.right, 2)

    assert_variable(test.right.args[0], 'bar')
    assert_variable(test.right.args[1], 'baz')


def test_function_kwargs():
    test = Plywood('foo(bar, 1, key="value")').compile()[0]
    assert_function(test, 'foo')
    assert_variable(test.left, 'foo')
    assert_parens(test.right, 2, 1)
    assert_variable(test.right.args[0], 'bar')
    assert_number(test.right.args[1], 1)
    assert_kvp(test.right.kwargs[0], 'key')
    assert_string(test.right.kwargs[0].value, 'value')


def test_autofunction():
    test = Plywood('foo bar, baz(a b), c=d').compile()[0]
    assert_function(test, 'foo')

    assert_variable(test.right.args[0], 'bar')
    assert_operator(test.right.args[1], '()')
    assert_kvp(test.right.kwargs[0], 'c')
    assert_variable(test.right.kwargs[0].value, 'd')


def test_dict():
    test = Plywood('{"foo": bar}').compile()[0]
    assert_dict(test, 1)
    assert_kvp(test.values[0], 'foo')
    assert_variable(test.values[0].value, 'bar')


def test_multiline_dict():
    test = Plywood('{\n  "foo": bar,\n  "quux": 0}').compile()[0]
    assert_dict(test, 2)
    assert_kvp(test.values[0], 'foo')
    assert_kvp(test.values[1], 'quux')
    assert_variable(test.values[0].value, 'bar')
    assert_number(test.values[1].value, 0)


def test_whitespace_dict():
    test_str = '''{
    "foo"
    :
    "bar"
    ,
}
'''
    test = Plywood(test_str).compile()[0]
    assert_dict(test, 1)

def test_empty_dict():
    test = Plywood('{\n    \n}').compile()[0]
    assert_dict(test, 0)


def test_dict_two():
    test = Plywood('{"foo": bar, bar: baz}').compile()[0]
    assert_dict(test, 2)
    assert_kvp(test.values[0], 'foo')
    assert_variable(test.values[0].value, 'bar')
    assert_kvp(test.values[1], PlywoodVariable(-1, 'bar'))
    assert_variable(test.values[1].value, 'baz')


def test_dict_multiline():
    test = Plywood('''{
        "foo": bar,
        "bar": baz
        }''').compile()[0]
    assert_dict(test, 2)
    assert_kvp(test.values[0], 'foo')
    assert_variable(test.values[0].value, 'bar')
    assert_kvp(test.values[1], PlywoodVariable(-1, 'bar'))
    assert_variable(test.values[1].value, 'baz')


def test_multiline_commands():
    test = Plywood("foo\nbar").compile()
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
""").compile()
    assert_variable(test[0], 'foo')
    assert_string(test[1], 'foo')
    assert_number(test[2], 1)
    assert_number(test[3], 123)
    assert_variable(test[4], 'bar')
    assert_operator(test[5], '()')


def test_block_indent_fail():
    with raises(ParseException):
        test = Plywood('   foo').compile()
        assert test == None


def test_block():
    test = Plywood('''
if True or False:
    print "True!"
''').compile()

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
''').compile()

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
''').compile()

    assert_block(test, 1)
    assert_function(test[0], 'div')
    assert_block(test[0].block, 1)
    assert_function(test[0].block[0], 'p')
    assert_block(test[0].block[0].block, 1)
    assert_string(test[0].block[0].block[0], 'text')


def test_classy_div():
    test = Plywood('''
div.classy: 'text'
''').compile()

    assert_block(test, 1)
    assert_function(test[0])
    assert_operator(test[0].left, '.')
    assert_variable(test[0].left.left, 'div')
    assert_variable(test[0].left.right, 'classy')
    assert_block(test[0].block, 1)
    assert_string(test[0].block[0], 'text')


def test_getitem():
    test = Plywood('''
div['something'] = 'text'
''').compile()

    assert_block(test, 1)
    assert_operator(test[0], '=')
    assert_operator(test[0].left, '[]')
    assert_variable(test[0].left.left, 'div')
    assert_indices(test[0].left.right, 1)
    assert_string(test[0].left.right[0], 'something')
    assert_string(test[0].right, 'text')


def test_getitem_2():
    test = Plywood('''
div['something']['else'] = 'text'
''').compile()

    assert_block(test, 1)
    assert_operator(test[0], '=')
    assert_operator(test[0].left, '[]')
    assert_operator(test[0].left.left, '[]')
    assert_variable(test[0].left.left.left, 'div')
    assert_indices(test[0].left.left.right, 1)
    assert_string(test[0].left.left.right[0], 'something')

    assert_indices(test[0].left.right, 1)
    assert_string(test[0].left.right[0], 'else')
    assert_string(test[0].right, 'text')


def test_getitem_getattr():
    test = Plywood('''
div['item'].attr['attritem'] = 'text'
''').compile()

    assert_block(test, 1)
    assert_operator(test[0], '=')
    assert_operator(test[0].left, '[]')
    assert_operator(test[0].left.left, '.')
    assert_operator(test[0].left.left.left, '[]')
    assert_variable(test[0].left.left.left.left, 'div')
    assert_indices(test[0].left.left.left.right, 1)
    assert_string(test[0].left.left.left.right.values[0], 'item')
    assert_indices(test[0].left.right, 1)
    assert_string(test[0].left.right[0], 'attritem')
    assert_string(test[0].right, 'text')


def test_multi_inline():
    test = Plywood('''
foo: bar
foo: bar
''').compile()
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
''').compile()
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
''').compile()
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
''').compile()
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
        plywood('''
foo:
    foo:
        BAH:  bar
        # too much indent:
          foo:  bar
''').compile()
        assert False


def test_multi_block_in_out():
    test = Plywood('''
foo:
    foo
BAH:
    BAH
''').compile()
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
''').compile()
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


def test_mixed_block_indented_last():
    test = Plywood('''
foo: bar:
        baz
''').compile()
    assert_block(test, 1)
    assert_function(test[0], 'foo')
    assert_block(test[0].block, 1)
    assert_block(test[0].block[0].block, 1)


def test_mixed_block_fail():
    with raises(ParseException):
        test = Plywood('''
foo:
    bar:
        baz
      baz
''').compile()
        assert test == None


def test_for_syntax():
    test = Plywood('''
for value in [1,2,3]:
    value
''').compile()
    assert_block(test, 1)
    assert_function(test[0], 'for')
    assert_parens(test[0].right, 1, 0)
    assert_operator(test[0].right.args[0], 'in')
    assert_variable(test[0].right.args[0].left, 'value')
    assert_list(test[0].right.args[0].right, 3)
    assert_block(test[0].block, 1)
    assert_variable(test[0].block[0], 'value')


def test_attr_call_precedence():
    test = Plywood('''
a.b()
''').compile()
    assert_block(test, 1)
    assert_function(test[0])
    assert_operator(test[0].left, '.')
    assert_variable(test[0].left.left, 'a')
    assert_variable(test[0].left.right, 'b')
