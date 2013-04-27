from . import assert_output


def test_reverse():
    input = '''
test = [1,2,3]
for t in reverse(test):
    t
'''
    desired = '''3
2
1
'''
    assert_output(input, desired)


def test_cdata():
    input = 'cdata("content")'
    desired = '<![CDATA[content]]>\n'
    assert_output(input, desired)
