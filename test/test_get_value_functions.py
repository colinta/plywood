# from pytest import raises
from plywood import plywood


def test_html_plugin():
    assert plywood('html') == '<html></html>'


def test_html_parens_plugin():
    assert plywood('html()') == '<html></html>'


def test_html_with_content():
    assert plywood('html: "content"') == '<html>\n    content\n</html>'


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
    output = '''<html>
    <title>
        A title!
    </title>
</html>'''
    assert plywood(input) == output


def test_nested_inline_tags():
    input = '''# a comment, for funsies.
html:
    title: "A title!"
    body:
        p: "some text"
        a(href="test"): 'anchor'
'''
    output = '''<html>
    <title>A title!</title>
    <body>
    </body>
</html>
'''
    assert plywood(input) == output
