from plywood import plywood
from difflib import unified_diff


def test_example_1():
    input = open('test/examples/example.ply').read()
    desired = open('test/examples/example_1.html').read()

    vals = {
        'title': 'Welcome!',
        'keywords': 'plywood',
        'persons': ['Joey', 'Joe', 'Shabbadoo'],
        }
    actual = plywood(input, vals, indent='  ')
    if actual != desired:
        diff = unified_diff(desired.splitlines(), actual.splitlines())
        print diff
        for line in diff:
            print line
    assert desired == actual


def test_example_2():
    input = open('test/examples/example.ply').read()
    desired = open('test/examples/example_2.html').read()

    vals = {
        'author': 'colin gray',
        }
    actual = plywood(input, vals, indent='  ')
    if actual != desired:
        diff = unified_diff(desired.splitlines(), actual.splitlines())
        print diff
        for line in diff:
            print line
    assert desired == actual
