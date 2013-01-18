from . import assert_output


def test_while():
    input = '''
item = 3
while item:
    'item: ' item
    item -= 1
'''
    desired = '''item: 3
item: 2
item: 1
'''
    assert_output(input, desired)


def test_while_break():
    input = '''
item = 3
while item:
    'item: ' item
    item -= 1
    break
'''
    desired = '''item: 3
'''
    assert_output(input, desired)


def test_while_continue():
    input = '''
item = 3
while item:
    item -= 1
    if item == 2:
        continue
    'item: ' item
'''
    desired = '''item: 1
item: 0
'''
    assert_output(input, desired)
