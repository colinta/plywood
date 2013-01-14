from . import assert_output


def test_include():
    input = '''
include 'test/include'
'''
    desired = 'this is my test\n'
    assert_output(input, desired, {'word': 'test'})


def test_include_scoped():
    input = '''
include 'test/include', word='foo'
'''
    desired = 'this is my foo\n'
    assert_output(input, desired, {'word': 'test'})
