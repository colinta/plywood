from pytest import raises
from plywood import (
    Plywood, PlywoodValue,
    PlywoodVariable, PlywoodString, PlywoodNumber,
    PlywoodOperator, PlywoodUnaryOperator,
    PlywoodParens, PlywoodList, PlywoodDict,
    PlywoodKvp, PlywoodFunction, PlywoodBlock,
    ParseException,
    )


def test_numeric():
    PlywoodNumber(2)
