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
    def plugin(scope, arguments, block, classes, id):
        args = arguments.args
        kwargs = arguments.kwargs
        mapped_kwargs = {}
        for item in kwargs:
            key = item.key.get_value(scope)
            value = item.value.get_value(scope)
            mapped_kwargs[key] = value

        if classes:
            mapped_kwargs.setdefault('class', '')
            if mapped_kwargs['class']:
                mapped_kwargs['class'] += ' '
            mapped_kwargs['class'] += ' '.join(classes)

        if id:
            mapped_kwargs['id'] = id

        eol = ''
        inside = block.get_value(scope)
        if inside and args:
            raise InvalidArguments("Passing a block *and* positional arguments is confusing.")

        if inside and not block.inline:
            inside = scope['__indent'](inside)
            inside = "\n" + inside.rstrip() + "\n"

        attrs = ''
        for key, value in mapped_kwargs.iteritems():
            if value is False:
                continue
            elif value is True:
                value = key
            attrs += ' ' + key
            attrs += '="' + entitize(value) + '"'

        tag_open = '<' + tag_name + attrs + '>'
        tag_close = '</' + tag_name + '>'
        if args:
            inside = tag_open + (tag_close + "\n" + tag_open).join(arg.get_value(scope) for arg in args) + tag_close
            if len(args) > 1:
                inside = scope['__indent'](inside)
            return inside
        else:
            return tag_open + inside + tag_close + eol


TAGS = [
    'html', 'p', 'div', 'script', 'style', 'title', 'head',
    'span', 'body', 'header', 'nav', 'ul', 'li', 'a', 'button',
    'input', 'textarea', 'select', 'option',
    'em', 'strong', 'i', 'b'
]
for tag in TAGS:
    register_html_plugin(tag)
register_html_plugin('p')
