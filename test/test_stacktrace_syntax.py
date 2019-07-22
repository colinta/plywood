from pytest import raises
from chomsky import ParseException
from plywood.exceptions import CompilationError
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


def test_parens():
    try:
        Plywood('(-foo + -bar').compile()[0]
    except CompilationError as e:
        pass

    # assert_parens(test, 1)

    # assert_operator(test.args[0], '+')
    # assert_unary(test.args[0].left, '-')
    # assert_variable(test.args[0].left.value, 'foo')
    # assert_unary(test.args[0].right, '-')
    # assert_variable(test.args[0].right.value, 'bar')
