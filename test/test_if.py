from . import assert_output


def test_if_1():
    input = '''
if 1 == 1:
    'true'
'''
    desired = 'true\n'
    assert_output(input, desired)


def test_if_2():
    input = '''
if 1 != 2:
    'true'
'''
    desired = 'true\n'
    assert_output(input, desired)


def test_if_3():
    input = '''
if 1 == 2:
    'false'
'''
    desired = ''
    assert_output(input, desired)


def test_if_selftest():
    input = '''
if self.test:
    'true'
'''
    desired = 'true\n'
    assert_output(input, desired, {'test': True})


def test_elif():
    input = '''
if self.falsey:
    'false'
elif self.truthy:
    'true'
'''
    desired = 'true\n'
    assert_output(input, desired, {'falsey': False, 'truthy': True})


def test_else():
    input = '''
if self.falsey:
    'false'
else:
    'true'
'''
    desired = 'true\n'
    assert_output(input, desired, {'falsey': False, 'truthy': True})


def test_elif_else():
    input = '''
if self.falsey:
    'false'
elif self.falsey:
    'falsey'
else:
    'true'
'''
    desired = 'true\n'
    assert_output(input, desired, {'falsey': False, 'truthy': True})
