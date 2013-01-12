from plywood import plywood


input = open('example.ply').read()
desired = open('example.html').read()


def test_example():
    actual = plywood(input, {'title': 'Welcome!'})
    print 'actual:', actual
    print 'desired:', desired
    assert actual == desired
