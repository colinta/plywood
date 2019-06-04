import datetime
from plywood import plywood
from difflib import unified_diff


def test_example_1():
    input = open('test/examples/example.ply').read()
    desired = open('test/examples/example_1.html').read()
    now = datetime.datetime.now()
    desired = desired.replace('DATE_YEAR', now.strftime('%Y'))

    vals = {
        'title': 'Welcome!',
        'keywords': 'plywood',
        'persons': ['Joey', 'Joe', 'Shabbadoo'],
        }
    actual = plywood(input, vals, indent='  ')
    if actual != desired:
        diff = unified_diff(desired.splitlines(), actual.splitlines())
    assert desired == actual


def test_example_2():
    input = open('test/examples/example.ply').read()
    desired = open('test/examples/example_2.html').read()
    now = datetime.datetime.now()
    desired = desired.replace('DATE_YEAR', now.strftime('%Y'))

    vals = {
        'author': 'colin gray',
        }
    actual = plywood(input, vals, indent='  ')
    if actual != desired:
        diff = unified_diff(desired.splitlines(), actual.splitlines())
    assert desired == actual
