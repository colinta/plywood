from pytest import raises
from chomsky import ParseException
from plywood.exceptions import KeyError as PlywoodKeyError
from plywood import (
    plywood, Plywood,
    )


def test_parens():
    code = """
a = 'a'
b
# c"""
    with raises(PlywoodKeyError) as e:
        plywood(code, defaults=False)
    assert str(e.value) == """No value for 'b'
At line 3:
    a = 'a'
>>> b
    # c
"""
