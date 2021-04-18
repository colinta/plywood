from pytest import raises
from chomsky import ParseException
from plywood.exceptions import PlywoodRuntimeError
from plywood import (
    plywood, Plywood,
    )


def test_parens():
    code = """
a = 'a'
b + a
# c"""
    with raises(PlywoodRuntimeError) as e:
        result = plywood(code, defaults=False)
        print(result)
    assert str(e.value) == """unsupported operand type(s) for +: 'NoneType' and 'str'
At line 3:
    a = 'a'
>>> b + a
    # c
"""
