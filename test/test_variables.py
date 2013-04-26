from . import assert_output


def test_cdata():
    input = 'self.andand\nself.is_safe'
    desired = 'andand\nTrue\n'
    assert_output(input, desired, {'andand': 'andand', 'is_safe': 'True'})
