# from pytest import raises
from plywood import PlywoodString
from plywood.scope import Scope
from . import assert_strings


def test_interpolation_1():
    s = PlywoodString(0, 'testing {{"strings"}}')
    assert_strings(s.python_value(Scope()), 'testing strings')


def test_interpolation_2():
    s = PlywoodString(0, 'testing {{self.vars}}')
    assert_strings(s.python_value(Scope({'self': {'vars': 'da_vars'}})), 'testing da_vars')


def test_interpolation_multiline():
    s = PlywoodString(0, '''
    testing {{
        if self.vars:
            self.vars
        }} is fun
''')
    assert_strings(s.python_value(Scope({'self': {'vars': 'da_vars'}})), '''
    testing da_vars is fun
''')
