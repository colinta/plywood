from pytest import raises
from chomsky import ParseException
from plywood.exceptions import CompilationError
from plywood import (
    plywood, Plywood,
    )


def test_parens():
    code = """
a = b
(-foo + -bar
"""
    with raises(CompilationError) as e:
        Plywood(code).compile()[0]

    assert e.value.buffer.position == len(code)
