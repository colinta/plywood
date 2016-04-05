# coding: utf-8
from . import assert_output


def test_reverse():
    input = '''
test = [1,2,3]
for t in reverse(test):
    t
for t in test|reverse:
    t
'''
    desired = '''3
2
1
3
2
1
'''
    assert_output(input, desired)


def test_len():
    input = 'len([1,2,3])\n"test"|len'
    desired = '3\n4\n'
    assert_output(input, desired)


def test_cdata():
    input = 'cdata("content")\n"content"|cdata'
    desired = '<![CDATA[content]]>\n<![CDATA[content]]>\n'
    assert_output(input, desired)


def test_e():
    input = 'e("<>&“”")\n"<>&“”" | e'
    desired = '&lt;&gt;&amp;&ldquo;&rdquo;\n&lt;&gt;&amp;&ldquo;&rdquo;\n'
    assert_output(input, desired)
