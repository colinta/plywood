# from pytest import raises
from plywood import plywood


def test_html_plugin():
    assert plywood('html') == '<html></html>'


def test_html_parens_plugin():
    assert plywood('html()') == '<html></html>'


def test_html_with_content():
    assert plywood('html: "content"') == '<html>content</html>'


def test_html_kwargs_plugin():
    assert plywood('html foo="bar"') == '<html foo="bar"></html>'


def test_html_args_plugin():
    assert plywood('html "is fun"') == '<html>is fun</html>'


def test_html_kwargs_parens_plugin():
    assert plywood('html(foo="bar")') == '<html foo="bar"></html>'


def test_html_args_parens_plugin():
    assert plywood('html("is neat!")') == '<html>is neat!</html>'


def test_nested_tags():
    input = '''# a comment, for funsies.
html:
    title:
        "A title!"
'''
    output = '''<html><title>A title!</title></html>'''
    assert plywood(input) == output


def test_nested_inline_tags():
    input = '''# a comment, for funsies.
html:
    title: "A title!"
    body:
        p: "some text"
'''
    output = '''<html>\n<title>A title!</title>\n<body><p>some text</p></body>\n</html>'''
    assert plywood(input) == output


def test_lotso_inlines():
    input = '''
p: span: em: 'text'
'''
    output = '<p><span><em>text</em></span></p>'
    assert plywood(input) == output


def test_class_shorthand():
    input = '''
p.important: span.warning.gray: em: 'text'
'''
    output = '<p class="important"><span class="warning gray"><em>text</em></span></p>'
    assert plywood(input) == output


def test_id_shorthand():
    input = '''
p@label1: 'text'
p@label2: 'text'
'''
    output = '<p id="label1">text</p><p id="label2">text</p>'
    assert plywood(input) == output


def test_class_id_shorthand():
    input = '''
p.section: span@warning.gray.span12: em: 'text'
'''
    output = '<p class="section"><span class="gray span12" id="warning"><em>text</em></span></p>'
    assert plywood(input) == output
