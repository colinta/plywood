from . import assert_output


def test_get_block():
    input = '''
block 'test':
    'this is my test'
get_block 'test'
'''
    desired = 'this is my test\n'
    assert_output(input, desired)


def test_get_block_default():
    input = '''
block 'test1':
    'this is test1'
get_block 'test1':
    'invisible'
get_block 'test2':
    'visible'
'''
    desired = 'this is test1\nvisible\n'
    assert_output(input, desired)


def test_layout_not_extended():
    input = '''include "test/layout"'''
    desired = '''
<nav><ul></ul></nav>
'''[1:]
    assert_output(input, desired)


def test_layout_extended_no_content():
    input = '''
extends "test/layout"
'''[1:]
    desired = '''
<nav><ul>
    <li><a href="/link-one">Link One</a></li>
</ul></nav>
'''[1:]
    assert_output(input, desired)
