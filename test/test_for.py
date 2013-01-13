from . import assert_output


def test_for():
    input = '''
for item in ['i', 't', 'e', 'm', 's', ]:
    item
'''
    desired = 'i\nt\ne\nm\ns\n'
    assert_output(input, desired)


def test_for_empty():
    input = '''
for item in []:
    item
empty:
    'empty'
'''
    desired = 'empty\n'
    assert_output(input, desired)


def test_for_empty_else_empty():
    input = '''
for item in []:
    item
empty:
    'empty'
else:
    'else'
'''
    desired = 'empty\n'
    assert_output(input, desired)


def test_for_empty_else_else():
    input = '''
for item in [1,2,3]:
    item
empty:
    'empty'
else:
    'else'
'''
    desired = '1\n2\n3\nelse\n'
    assert_output(input, desired)


def test_for_else():
    input = '''
for item in [1, 2, 3]:
    item
else:
    'else'
'''
    desired = '1\n2\n3\nelse\n'
    assert_output(input, desired)


def test_for_break():
    input = '''
for item in [1, 2, 3]:
    item
    if item == 2:
        break
'''
    desired = '1\n2\n'
    assert_output(input, desired)


def test_for_continue():
    input = '''
for item in [1, 2, 3]:
    if item == 2:
        continue
    item
'''
    desired = '1\n3\n'
    assert_output(input, desired)


def test_for_nested_break():
    input = '''
for item1 in [1, 2, 3]:
    if item1 == 2:
        continue
    item1
    for item2 in 'abcd':
        if item2 == 'c':
            break
        item2
'''
    desired = '1\na\nb\n3\na\nb\n'
    assert_output(input, desired)
