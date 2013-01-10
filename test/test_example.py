from pytest import raises
from plywood import (
    Plywood, PlywoodValue,
    PlywoodVariable, PlywoodString, PlywoodNumber,
    PlywoodOperator, PlywoodUnaryOperator,
    PlywoodParens, PlywoodList, PlywoodDict,
    PlywoodKvp, PlywoodFunction, PlywoodBlock,
    ParseException,
    )


def assert_number(test, value):
    assert isinstance(test, PlywoodNumber)
    assert isinstance(test.value, type(value))
    assert test.value == value


def assert_string(test, value):
    assert isinstance(test, PlywoodString)
    assert test.value == value


def assert_variable(test, name):
    assert isinstance(test, PlywoodVariable)
    assert test.name == name


def assert_unary(test, op):
    assert isinstance(test, PlywoodUnaryOperator)
    assert test.operator == op


def assert_operator(test, op):
    assert isinstance(test, PlywoodOperator)
    assert test.operator == op


def assert_kvp(test, key):
    assert isinstance(test, PlywoodKvp)
    if key:
        if not isinstance(key, PlywoodValue):
            assert_string(test.key, key)
        else:
            assert test.key == key


def assert_block(test, count=None):
    assert isinstance(test, PlywoodBlock)
    if count is not None:
        assert len(test.lines) == count


def assert_parens(test, count=None):
    assert isinstance(test, PlywoodParens)
    if count is not None:
        assert len(test.args) == count


def assert_dict(test, count=None):
    assert isinstance(test, PlywoodDict)
    if count is not None:
        assert len(test.values) == count


example = """
# twitter bootstrap layout
doctype(5)
html:
  head:
    title: title
    script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js')
    link(rel='stylesheet', href='http://twitter.github.com/bootstrap/1.4.0/bootstrap.min.css')
    block 'head'

  body:
    div.container:
      div@page_header
      div.row:
        div.span6:
          block 'yield'

    div.container:
      footer:
        p "&copy; Simple Energy {date('%Y')}"
    script(type='text/javascript'):
      '''javascript
      $(document).ready(function(){

        $(".rounded-img").load(function() {
          $(this).wrap(function(){
            return '<span class="' + $(this).attr('class') + '" style="background:url(' + $(this).attr('src') + ') no-repeat center center; width: ' + $(this).width() + 'px; height: ' + $(this).height() + 'px;" />';
          });
          $(this).css("opacity", "0");
        });

      });
      '''
"""[1:-1]


def test_example():
    test = Plywood(example).parse()
    print
    print str(test)
    print
