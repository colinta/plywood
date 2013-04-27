from plywood.exceptions import InvalidArguments
from plywood.util import entitize


def output_element(scope, arguments, block, tag_name, classes, is_self_closing):
    args = arguments.args
    kwargs = arguments.kwargs

    if len(block.lines) and args:
        raise InvalidArguments("Passing a block *and* positional arguments is confusing.")

    if is_self_closing and args:
        raise InvalidArguments("Passing args to a self closing tag is confusing.")

    kwargs_class = ''
    for item in kwargs:
        key = item.key.python_value(scope)
        if key in ['class']:
            value = item.value.python_value(scope)
            if key == 'class':
                kwargs_class = value

    if classes and kwargs_class:
        classes.append(kwargs_class)

    inside = block.python_value(scope)
    if not block.inline and inside:
        inside = scope['__runtime'].indent(inside)
        inside = "\n" + inside.rstrip() + "\n"

    attrs = ''
    for item in kwargs:
        key = item.key.python_value(scope)
        if key == 'class':
            continue
        value = item.value.python_value(scope)
        if value is False:
            continue
        elif value is True:
            value = key
        attrs += ' ' + key
        attrs += '="' + entitize(value) + '"'

    if classes:
        attrs += ' class="' + ' '.join(classes) + '"'

    if is_self_closing:
        return '<' + tag_name + attrs + ' />'
    else:
        tag_open = '<' + tag_name + attrs + '>'
        tag_close = '</' + tag_name + '>'
        if args:
            inside = ''.join(arg.python_value(scope) for arg in args)
            if len(args) > 1:
                inside = scope['__runtime'].indent(inside)
        return tag_open + inside + tag_close
