# from pytest import raises
from plywood import plywood
from . import assert_output


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


def test_lotso_inlines_block():
    input = '''
p: span:
    em: 'text'
'''
    desired = "<p><span>\n    <em>text</em>\n</span></p>\n"
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
@label2: 'text'
'''
    desired = '<p id="label1">text</p>\n<div id="label2">text</div>\n'
    assert_output(input, desired)


def test_class_id_shorthand():
    input = '''
p.section: span@warning.gray.span12: em: 'text'
'''
    desired = '<p class="section"><span class="gray span12" id="warning"><em>text</em></span></p>\n'
    assert_output(input, desired)
