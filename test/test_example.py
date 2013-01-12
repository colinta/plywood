from plywood import plywood


input = open('test/example.ply').read()
desired = open('test/example.html').read()


def test_example():
    actual = plywood(input, {'title': 'Welcome!'}, indent='  ')
    print 'actual:', actual
    print 'desired:', desired
    assert actual == desired
