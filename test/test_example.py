from plywood import plywood
from difflib import unified_diff


input = open('test/example.ply').read()
desired = open('test/example.html').read()


def test_example():
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
