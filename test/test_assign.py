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


def test_bitwise_or_assign():
    input = '''
test = 3
test |= 9
test
'''
    desired = '11\n'
    assert_output(input, desired)


def test_bitwise_and_assign():
    input = '''
test = 13
test &= 11
test
'''
    desired = '9\n'
    assert_output(input, desired)


def test_boolean_or_assign():
    input = '''
test = False
test or= 10
test
'''
    desired = '10\n'
    assert_output(input, desired)


def test_boolean_and_assign():
    input = '''
test = True
test and= 11
test
'''
    desired = '11\n'
    assert_output(input, desired)
