# from pytest import raises
from plywood import plywood


def assert_output(input, desired):
    actual = plywood(input)
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_html_plugin():
    assert plywood('html') == "<html></html>\n"


def test_html_parens_plugin():
    assert plywood('html()') == "<html></html>\n"


def test_html_with_content():
    assert plywood('html: "content"') == "<html>content</html>\n"


def test_html_kwargs_plugin():
    assert plywood('html foo="bar"') == "<html foo=\"bar\"></html>\n"


def test_html_args_plugin():
    assert plywood('html "is fun"') == "<html>is fun</html>\n"


def test_html_kwargs_parens_plugin():
    assert plywood('html(foo="bar")') == "<html foo=\"bar\"></html>\n"


def test_html_args_parens_plugin():
    assert plywood('html("is neat!")') == "<html>is neat!</html>\n"


def test_nested_tags():
    input = '''# a comment, for funsies.
html:
    title:
        "A title!"
'''
    desired = '''<html>
    <title>
        A title!
    </title>
</html>
'''
    assert_output(input, desired)


def test_nested_inline_tags():
    input = '''# a comment, for funsies.
html:
    title: "A title!"
    body:
        p: "some text"
'''
    desired = '''<html>
    <title>A title!</title>
    <body>
        <p>some text</p>
    </body>
</html>
'''
    assert_output(input, desired)


def test_lotso_inlines():
    input = '''
p: span: em: 'text'
'''
    desired = "<p><span><em>text</em></span></p>\n"
    assert_output(input, desired)


def test_class_shorthand():
    input = '''
p.important: span.warning.gray: em: 'text'
'''
    desired = '<p class="important"><span class="warning gray"><em>text</em></span></p>\n'
    assert_output(input, desired)


def test_id_shorthand():
    input = '''
p@label1: 'text'
p@label2: 'text'
'''
    desired = '<p id="label1">text</p>\n<p id="label2">text</p>\n'
    assert_output(input, desired)


def test_class_id_shorthand():
    input = '''
p.section: span@warning.gray.span12: em: 'text'
'''
    desired = '<p class="section"><span class="gray span12" id="warning"><em>text</em></span></p>\n'
    assert_output(input, desired)


def test_if_1():
    input = '''
if 1 == 1:
    'true'
'''
    desired = 'true\n'
    actual = plywood(input)
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_if_2():
    input = '''
if 1 != 2:
    'true'
'''
    desired = 'true\n'
    actual = plywood(input)
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_if_3():
    input = '''
if 1 == 2:
    'false'
'''
    desired = ''
    actual = plywood(input)
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_if_selftest():
    input = '''
if self.test:
    'true'
'''
    desired = 'true\n'
    actual = plywood(input, {'test': True})
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_elif():
    input = '''
if self.falsey:
    'false'
elif self.truthy:
    'true'
'''
    desired = 'true\n'
    actual = plywood(input, {'falsey': False, 'truthy': True})
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_else():
    input = '''
if self.falsey:
    'false'
else:
    'true'
'''
    desired = 'true\n'
    actual = plywood(input, {'falsey': False, 'truthy': True})
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


def test_elif_else():
    input = '''
if self.falsey:
    'false'
elif self.falsey:
    'falsey'
else:
    'true'
'''
    desired = 'true\n'
    actual = plywood(input, {'falsey': False, 'truthy': True})
    print 'actual:', actual
    print 'desired:', desired
    assert desired == actual


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
