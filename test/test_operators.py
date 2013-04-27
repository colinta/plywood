from . import assert_output
from plywood.env import PlywoodEnv


def test_plus_operator():
    input = 'a + b'
    desired = '3\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2})


def test_minus_operator():
    input = 'a - b'
    desired = '3\n'
    assert_output(input, desired, globals={'a': 5, 'b': 2})


def test_times_operator():
    input = 'a * b'
    desired = '10\n'
    assert_output(input, desired, globals={'a': 5, 'b': 2})


def test_exponent_operator():
    input = 'a ** b'
    desired = '8\n'
    assert_output(input, desired, globals={'a': 2, 'b': 3})


def test_divide_operator():
    input = 'a / b'
    desired = '9.0\n'
    assert_output(input, desired, globals={'a': 63, 'b': 7})


def test_int_divide_operator():
    input = 'a // b'
    desired = '5\n'
    assert_output(input, desired, globals={'a': 11, 'b': 2})


def test_eq_operator():
    input = 'a == b\na == c'
    desired = 'False\nTrue\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1})


def test_ne_operator():
    input = 'a != b\na != c'
    desired = 'True\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1})


def test_lte_operator():
    input = 'a <= b\na <= c\na <= d'
    desired = 'True\nTrue\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1, 'd': 0})


def test_lt_operator():
    input = 'a < b\na < c\na < d'
    desired = 'True\nFalse\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1, 'd': 0})


def test_gt_operator():
    input = 'a > b\na > c\na > d'
    desired = 'False\nFalse\nTrue\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1, 'd': 0})


def test_gte_operator():
    input = 'a >= b\na >= c\na >= d'
    desired = 'False\nTrue\nTrue\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1, 'd': 0})


def test_in_operator():
    input = 'a in b\na in c'
    desired = 'True\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': [1, 2], 'c': [0, 2]})


def test_is_operator():
    input = 'a is b\na is c\na is d'
    desired = 'False\nTrue\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': 1, 'd': True})


def test_and_operator():
    input = 'a and b\na and c'
    desired = 'True\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': True, 'c': False})


def test_or_operator():
    input = 'a or b\nc or b\nc or d'
    desired = '1\nTrue\n0\n'
    assert_output(input, desired, globals={'a': 1, 'b': True, 'c': False, 'd': 0})


def test_pipe_operator():
    input = 'a | reverse'
    desired = 'dcba\n'
    assert_output(input, desired, globals={'a': 'abcd'})


@PlywoodEnv.register_fn()
def pipe2_test(contents, l, r=None):
    r = r or l
    return l + contents + r


def test_pipe2_operator():
    input = '''a | reverse | pipe2_test("->", "<-")
a | reverse | pipe2_test("|")
'''
    desired = '->dcba<-\n|dcba|\n'
    assert_output(input, desired, globals={'a': 'abcd'})


def test_modulus_operator():
    input = 'a % b'
    desired = '2\n'
    assert_output(input, desired, globals={'a': 11, 'b': 3})


def test_getitem_operator():
    input = 'a[b]'
    desired = 'Bee\n'
    assert_output(input, desired, globals={'a': {'bee': 'Bee'}, 'b': 'bee'})


def test_getattr_operator():
    class Dummy(object):
        pass
    a = Dummy()
    a.b = 'bee'
    input = 'a.b'
    desired = 'bee\n'
    assert_output(input, desired, globals={'a': a})


def test_unary_dot_operator():
    input = '.a\n.b'
    desired = '<div class="a"></div>\n<div class="b"></div>\n'
    assert_output(input, desired, globals={})


def test_unary_negate_operator():
    input = '-a\n-b'
    desired = '-1\n2\n'
    assert_output(input, desired, globals={'a': 1, 'b': -2})


def test_unary_not_operator():
    input = 'not a\nnot b'
    desired = 'False\nTrue\n'
    assert_output(input, desired, globals={'a': True, 'b': False})


def test_assign_operator():
    input = 'a = b\na\nb'
    desired = '2\n2\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2})


def test_plus_equals_operator():
    input = 'a += b\na\nb'
    desired = '3\n2\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2})


def test_minus_equals_operator():
    input = 'a -= b\na\nb'
    desired = '-1\n2\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2})


def test_times_equals_operator():
    input = 'a *= b\na\nb'
    desired = '8\n2\n'
    assert_output(input, desired, globals={'a': 4, 'b': 2})


def test_exponent_equals_operator():
    input = 'a **= b\na\nb'
    desired = '16\n2\n'
    assert_output(input, desired, globals={'a': 4, 'b': 2})


def test_divide_equals_operator():
    input = 'a /= b\na\nb'
    desired = '5.0\n2\n'
    assert_output(input, desired, globals={'a': 10, 'b': 2})


def test_int_divide_equals_operator():
    input = 'a //= b\na\nb'
    desired = '5\n2\n'
    assert_output(input, desired, globals={'a': 11, 'b': 2})


def test_modulus_equals_operator():
    input = 'a %= b\na\nb'
    desired = '2\n3\n'
    assert_output(input, desired, globals={'a': 11, 'b': 3})


def test_or_equals_operator():
    input = 'a or= b\nc or= b\na\nb\nc'
    desired = '1\n2\n2\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': False})


def test_and_equals_operator():
    input = 'a and= b\nc and= b\na\nb\nc'
    desired = '2\n2\nFalse\n'
    assert_output(input, desired, globals={'a': 1, 'b': 2, 'c': False})
