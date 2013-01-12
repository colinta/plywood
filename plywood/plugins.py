import sys
from values import PlywoodValue
from util import entitize
from exceptions import InvalidArguments


@PlywoodValue.register_fn('print')
def print_(scope, arguments, block):
    args = arguments.args
    kwargs = arguments.kwargs
    sys.stderr.write(repr(args), repr(kwargs))
    sys.stderr.write("\n")
    return block.get_value(scope)


DOCTYPES = {
    '5': '<!DOCTYPE html>\n',
    'default': '<!DOCTYPE html>\n',
    'xml': '<?xml version="1.0" encoding="utf-8" ?>\n',
    'transitional': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n',
    'strict': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n',
    'frameset': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">\n',
    '1.1': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n',
    'basic': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">\n',
    'mobile': '<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">\n',
    '4': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n',
    'html4': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n',
    'transitional4': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n',
    'frameset4': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">\n',
}


@PlywoodValue.register_fn()
def doctype(scope, arguments, block):
    try:
        doctype = arguments.args[0].get_value(scope)
    except IndexError:
        doctype = '5'
    return DOCTYPES.get(doctype, doctype)


def register_html_plugin(tag_name, is_block=False, self_closing=False):
    @PlywoodValue.register_plugin(tag_name)
    def plugin(scope, arguments, block, classes, id):
        args = arguments.args
        kwargs = arguments.kwargs

        if len(block.lines) and args:
            raise InvalidArguments("Passing a block *and* positional arguments is confusing.")

        if self_closing and args:
            raise InvalidArguments("Passing args to a self closing tag is confusing.")

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

        inside = block.get_value(scope)
        print("""=============== plugins.py at line {0} ===============
tag_name: {5!r}
is_block: {1!r}
inside: {2!r}
inner block: {3!r}
outer block: {4!r}
""".format(__import__('sys')._getframe().f_lineno - 6, is_block, inside, block.inline and 'inline' or 'block', scope['__block'].inline and 'inline' or 'block', tag_name))
        if not block.inline and inside:
            print("=============== plugins.py at line {0} ===============".format(__import__('sys')._getframe().f_lineno))
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

        if self_closing:
            return '<' + tag_name + inside + ' />'
        else:
            tag_open = '<' + tag_name + attrs + '>'
            tag_close = '</' + tag_name + '>'
            if args:
                inside = ''.join(arg.get_value(scope) for arg in args)
                if len(args) > 1:
                    inside = scope['__indent'](inside)
            return tag_open + inside + tag_close


def register_self_closing_plugin(tag_name):
    pass


from tags import BLOCK_TAGS, INLINE_TAGS, SELF_CLOSING

for tag in BLOCK_TAGS:
    register_html_plugin(tag, is_block=True)

for tag in INLINE_TAGS:
    register_html_plugin(tag, is_block=False)

for tag in SELF_CLOSING:
    register_html_plugin(tag, self_closing=True)
