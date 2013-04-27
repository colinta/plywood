from . import assert_output


def test_auto_product():
    input = '''
three = 3
six = 2 three
six
'''
    desired = '6\n'
    assert_output(input, desired)
