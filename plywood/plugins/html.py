from plywood.env import PlywoodEnv
from plywood.util import entitize
from plywood.exceptions import InvalidArguments


def register_html_plugin(tag_name, is_block=False, self_closing=False):
    @PlywoodEnv.register_html_plugin(tag_name)
    def plugin(scope, arguments, block, classes, id):
        args = arguments.args
        kwargs = arguments.kwargs

        if len(block.lines) and args:
            raise InvalidArguments("Passing a block *and* positional arguments is confusing.")

        if self_closing and args:
            raise InvalidArguments("Passing args to a self closing tag is confusing.")

        kwargs_class = ''
        for item in kwargs:
            key = item.key.get_value(scope)
            value = item.value.get_value(scope)
            if key == 'class':
                kwargs_class = value
            elif key == 'id':
                id = value

        if classes and kwargs_class:
            classes.append(kwargs_class)

        inside = block.python_value(scope)
        if not block.inline and inside:
            inside = scope['__indent'](inside)
            inside = "\n" + inside.rstrip() + "\n"

        attrs = ''
        for item in kwargs:
            key = item.key.python_value(scope)
            if key == 'class' or key == 'id':
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
        if id:
            attrs += ' id="' + id + '"'

        if self_closing:
            return '<' + tag_name + attrs + ' />'
        else:
            tag_open = '<' + tag_name + attrs + '>'
            tag_close = '</' + tag_name + '>'
            if args:
                inside = ''.join(arg.python_value(scope) for arg in args)
                if len(args) > 1:
                    inside = scope['__indent'](inside)
            return tag_open + inside + tag_close
    plugin.__name__ = tag_name


def register_self_closing_plugin(tag_name):
    pass


from tags import BLOCK_TAGS, INLINE_TAGS, SELF_CLOSING

for tag in BLOCK_TAGS:
    register_html_plugin(tag, is_block=True)

for tag in INLINE_TAGS:
    register_html_plugin(tag, is_block=False)

for tag in SELF_CLOSING:
    register_html_plugin(tag, self_closing=True)
