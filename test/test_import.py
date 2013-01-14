import os
from . import assert_output


def test_import_1():
    input = '''
import os
os.getcwd()
'''
    desired = os.getcwd() + '\n'
    assert_output(input, desired)


def test_import_2():
    input = '''
import os
os.getcwd
'''
    desired = os.getcwd() + '\n'
    assert_output(input, desired)


def test_import_3():
    input = '''
import os.path
os.path.expanduser('~')
'''
    desired = os.path.expanduser('~') + '\n'
    assert_output(input, desired)


def test_from():
    input = '''
from os import (getcwd,path)
getcwd()
path.join(getcwd, 'test')
'''
    desired = os.getcwd() + '\n' + os.path.join(os.getcwd(), 'test') + '\n'
    assert_output(input, desired)
