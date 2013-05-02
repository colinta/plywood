from . import assert_output


def test_get_block():
    input = '''
block 'test':
    'this is my test'
get_block 'test'
'''
    desired = 'this is my test\n'
    assert_output(input, desired)


def test_get_block_override_second():
    input = '''
block 'test':
    'this is my test'
block 'test':
    'this is overridden'
get_block 'test'
'''
    desired = 'this is overridden\n'
    assert_output(input, desired)


def test_get_block_default():
    input = '''
block 'test1':
    'overrides'
get_block 'test1':
    'content'
get_block 'test2':
    'visible'
'''
    desired = 'overrides\nvisible\n'
    assert_output(input, desired)


def test_layout_not_extended():
    input = '''include "test/examples/layout"'''
    desired = '''
<nav><ul></ul></nav>
'''[1:]
    assert_output(input, desired)


def test_layout_extended_no_content():
    input = '''
extends "test/examples/layout"
'''[1:]
    desired = '''
<nav><ul>
    <li><a href="/link-one">Link One</a></li>
</ul></nav>
'''[1:]
    assert_output(input, desired)


def test_layout_extended_with_content():
    input = '''
extends "test/examples/layout":
    h1: 'this post is great!'
'''[1:]
    desired = '''
<nav><ul>
    <li><a href="/link-one">Link One</a></li>
</ul></nav>
<h1>this post is great!</h1>
'''[1:]
    assert_output(input, desired)


def test_layout_extended_with_super():
    input = '''
extends "test/examples/layout":
    block 'nav':
        super
        li: hr
    h1: 'this post is great!'
'''[1:]
    desired = '''
<nav><ul>
    <li><a href="/link-one">Link One</a></li>
    <li><hr /></li>
</ul></nav>
<h1>this post is great!</h1>
'''[1:]
    assert_output(input, desired)


def test_layout_extended_locals():
    input = '''
extends "test/examples/layout"
'''[1:]
    desired = '''
<nav><ul>
    <li><a href="/">Home</a></li>
</ul></nav>
'''[1:]
    assert_output(input, desired, {'links': [{'href': '/', 'title': 'Home'}]})


def test_layout_nested():
    input = '''
extends "test/examples/nested_layout":
  # block 'nav':
  #   li: 'outmost pre'
  #   super
  #   li: 'outmost post'
  'neat!'
'''[1:]
    desired = '''
<nav><ul>
    <li>outmost pre</li>
    <li>pre</li>
    <li><a href="/link-one">Link One</a></li>
    <li>post</li>
    <li>outmost post</li>
</ul></nav>
neat!
'''[1:]
    assert_output(input, desired)
