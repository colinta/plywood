# from pytest import raises
from plywood import plywood, PlywoodString
from . import assert_output, assert_strings


def test_interpolation_1():
    s = PlywoodString(0, 'testing {{"strings"}}')
    assert_strings(s.python_value({}), 'testing strings')


def test_interpolation_2():
    s = PlywoodString(0, 'testing {{self.vars}}')
    assert_strings(s.python_value({'vars': 'da_vars'}), 'testing da_vars')


def test_interpolation_multiline():
    s = PlywoodString(0, '''
    testing {{
        if self.vars:
            self.vars
        }} is fun
''')
    assert_strings(s.python_value({'vars': 'da_vars'}), '''
    testing da_vars is fun
''')
