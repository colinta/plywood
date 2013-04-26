from . import assert_output


def test_include():
    input = '''
include 'test/examples/include'
'''
    desired = 'this is my test\n'
    assert_output(input, desired, {'word': 'test'})


def test_include_function():
    input = '''
include 'test/examples/include_function'
foo()
foo('bar')
'''
    desired = 'footest\nfoo\nfoobar\n'
    assert_output(input, desired)


def test_include_variables():
    input = '''
self.word
include 'test/examples/include_variables'
self.word
'''
    desired = 'test\nword changed\n'
    assert_output(input, desired, {'word': 'test'})


def test_include_scoped():
    input = '''
include 'test/examples/include', word='foo'
'this is my ' + self.word
'''
    desired = 'this is my foo\nthis is my test\n'
    assert_output(input, desired, {'word': 'test'})
