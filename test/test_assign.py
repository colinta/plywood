from . import assert_output


def test_assign():
    input = '''
test = 'value'
test
'''
    desired = 'value\n'
    assert_output(input, desired)


def test_assign_chain():
    input = '''
test1 = test2 = 'value'
test1
test2
'''
    desired = 'value\nvalue\n'
    assert_output(input, desired)


def test_setattr():
    class Dummy():
        pass
    dummy = Dummy()
    dummy.property = 'old value'
    input = '''
self.dummy.property
self.dummy.property = 'new value'
self.dummy.property
'''
    desired = 'old value\nnew value\n'
    assert_output(input, desired, {'dummy': dummy})


def test_setattr_nested():
    class Dummy(object):
        pass
    dummy = Dummy()
    nested = Dummy()
    nested.property = 'old value'
    dummy.nested = nested
    input = '''
self.dummy.nested.property
self.dummy.nested.property = 'new value'
self.dummy.nested.property
'''
    desired = 'old value\nnew value\n'
    assert_output(input, desired, {'dummy': dummy})


def test_setitem():
    dummy = {
        'property': 'old value',
    }
    input = '''
self.dummy["property"]
self.dummy["property"] = 'new value'
self.dummy["property"]
'''
    desired = 'old value\nnew value\n'
    assert_output(input, desired, {'dummy': dummy})


def test_setitem_nested():
    dummy = {
        'nested': {'property': 'old value'},
    }
    input = '''
self.dummy['nested']['property']
self.dummy['nested']['property'] = 'new value'
self.dummy['nested']['property']
'''
    desired = 'old value\nnew value\n'
    assert_output(input, desired, {'dummy': dummy})


def test_plus_assign():
    input = '''
test = 3
test += 2
test
'''
    desired = '5\n'
    assert_output(input, desired)


def test_minus_assign():
    input = '''
test = 4
test -= 1
test
'''
    desired = '3\n'
    assert_output(input, desired)


def test_times_assign():
    input = '''
test = 5
test *= 2
test
'''
    desired = '10\n'
    assert_output(input, desired)


def test_power_assign():
    input = '''
test = 6
test **= 3
test
'''
    desired = '216\n'
    assert_output(input, desired)


def test_divide_assign():
    input = '''
test = 22
test /= 4
test
'''
    desired = '5.5\n'
    assert_output(input, desired)


def test_int_divide_assign():
    input = '''
test = 81
test //= 5
test
'''
    desired = '16\n'
    assert_output(input, desired)


def test_modulo_assign():
    input = '''
test = 9
test %= 4
test
'''
    desired = '1\n'
    assert_output(input, desired)


def test_boolean_or_assign():
    input = '''
test1 = 20
test1 or= 10
test2 = False
test2 or= 10
test1
test2
'''
    desired = '20\n10\n'
    assert_output(input, desired)


def test_boolean_and_assign():
    input = '''
test1 = 0
test1 and= 11
test2 = True
test2 and= 11
test1
test2
'''
    desired = '0\n11\n'
    assert_output(input, desired)
