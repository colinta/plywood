from . import assert_output


# these variables were giving me trouble because 'is' and 'and' are operators
def test_variables():
    input = 'andand\nis_safe\nnota'
    desired = 'andand\nTrue\nisa\n'
    assert_output(input, desired, globals={'andand': 'andand', 'is_safe': 'True', 'nota': 'isa'})
