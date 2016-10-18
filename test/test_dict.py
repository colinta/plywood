from pytest import raises
from . import assert_output


def test_dict():
    input = '''
test = {'key': 'value'}
'''
    desired = ''
    assert_output(input, desired)


def test_empty_dict():
    input = '''
test = {}
'''
    desired = ''
    assert_output(input, desired)


def test_multiline_dict():
    input = '''
test = {
    'key': 'value'
}
'''
    desired = ''
    assert_output(input, desired)


def test_multiline_empty_dict():
    input = '''
test = {
}
'''
    desired = ''
    assert_output(input, desired)


def test_dict_getitem():
    dummy = {}
    dummy['property'] = 'value'
    input = '''
self.dummy["property"]
'''
    desired = 'value\n'
    assert_output(input, desired, {'dummy': dummy})


def test_dict_getattr():
    dummy = {}
    dummy['property'] = 'value'
    input = '''
self.dummy.property
'''
    desired = 'value\n'
    assert_output(input, desired, {'dummy': dummy})
