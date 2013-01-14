from . import assert_output


def test_ieif():
    input = '''
ieif 'lt IE 9':
    link(rel='stylesheet', type='text/css', href='css/ie.css')
'''
    desired = '''<!--[if lt IE 9]>
    <link rel="stylesheet" type="text/css" href="css/ie.css" />
<![endif]-->
'''
    assert_output(input, desired)


def test_ieif_indented():
    input = '''
head:
    ieif 'lt IE 9':
        link(rel='stylesheet', type='text/css', href='css/ie.css')
'''
    desired = '''<head>
    <!--[if lt IE 9]>
        <link rel="stylesheet" type="text/css" href="css/ie.css" />
    <![endif]-->
</head>
'''
    assert_output(input, desired)
