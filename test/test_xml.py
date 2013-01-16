from . import assert_output


def test_xml_attribute():
    input = '''
div(xmlns='urn:loc.gov:books',
    xmlns:isbn='urn:ISBN:0-395-36341-6')
'''
    desired = '''<div xmlns="urn:loc.gov:books" xmlns:isbn="urn:ISBN:0-395-36341-6"></div>\n'''
    assert_output(input, desired)


def test_xml_constructor():
    input = '''
<book xmlns='urn:loc.gov:books',
      xmlns:isbn='urn:ISBN:0-395-36341-6'>:
    <isbn:number>: 1568491379
'''
    desired = '''<div xmlns="urn:loc.gov:books" xmlns:isbn="urn:ISBN:0-395-36341-6"></div>\n'''
    assert_output(input, desired)
