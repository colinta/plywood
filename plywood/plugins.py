import sys
from values import PlywoodValue
from util import entitize
from exceptions import InvalidArguments


@PlywoodValue.register_fn('print')
def print_(scope, arguments, block):
    args = arguments.args
    kwargs = arguments.kwargs
    sys.stderr.write(repr(args), repr(kwargs)) + (block and block.run(scope) or '')
    sys.stderr.write("\n")
    return block.get_value(scope)


def register_html_plugin(tag_name):
    @PlywoodValue.register_plugin(tag_name)
    def plugin(scope, arguments, block):
        args = arguments.args
        kwargs = arguments.kwargs

        eol = ''
        inside = block.get_value(scope)
        if inside and args:
            raise InvalidArguments("Passing a block *and* positional arguments is confusing.")
        elif args:
            inside = "\n".join(arg.get_value(scope) for arg in args)
            if len(args) > 1:
                inside = scope['__indent'](inside)
                eol = '\n'
        elif inside:
            inside = scope['__indent'](inside)
            inside = "\n" + inside + "\n"

        attrs = ''
        for item in kwargs:
            key = item.key.get_value(scope)
            value = item.value.get_value(scope)
            if value is False:
                continue
            elif value is True:
                value = key
            attrs += ' ' + key
            attrs += '="' + entitize(value) + '"'

        return '<' + tag_name + attrs + '>' + inside + '</' + tag_name + '>' + eol


TAGS = [
    'html', 'p', 'div', 'script', 'style', 'title', 'head',
    'span', 'body', 'header', 'nav', 'ul', 'li', 'a', 'button',
    'input', 'textarea', 'select', 'option',
]
for tag in TAGS:
    register_html_plugin(tag)
register_html_plugin('p')
