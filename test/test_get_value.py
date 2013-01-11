# from pytest import raises
from plywood import plywood


def test_numeric():
    assert plywood('2') == '2'


def test_numeric_parens():
    assert plywood('(2)') == '2'


def test_unary():
    assert plywood('-(2)') == '-2'


def test_string():
    assert plywood('"test"') == 'test'


def test_float():
    assert plywood('1.23') == '1.23'


def test_addition():
    assert plywood('1+1') == '2'


def test_multiplication():
    assert plywood('2*3') == '6'


def test_division():
    assert plywood('3/6') == '0.5'


def test_division_integer():
    assert plywood('6//5') == '1'


def test_power():
    assert plywood('3**2') == '9'
