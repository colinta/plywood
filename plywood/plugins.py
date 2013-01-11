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


@PlywoodValue.register_plugin()
def doctype(doctype='default'):
    return DOCTYPES.get(doctype, doctype)


def register_html_plugin(tag_name, is_block=False, self_closing=False):
    @PlywoodValue.register_plugin(tag_name)
    def plugin(scope, arguments, block, classes, id):
        args = arguments.args
        kwargs = arguments.kwargs

        if len(block.lines) and args:
            raise InvalidArguments("Passing a block *and* positional arguments is confusing.")

        if not is_block and args:
            raise InvalidArguments("Passing args to an inline argument.")

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
        if is_block and inside:
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
                inside = tag_open + (tag_close + (is_block and "\n" or '') + tag_open).join(arg.get_value(scope) for arg in args) + tag_close
                if len(args) > 1:
                    inside = scope['__indent'](inside)
                return inside
            else:
                return tag_open + inside + tag_close + eol


def register_self_closing_plugin(tag_name):
    pass


BLOCK_TAGS = [
  'address',   'blockquote',
  'center',    'dl',
  'dt',        'dd',
  'div',       'dir',
  'head',      'h1',
  'h2',        'h3',
  'h4',        'h5',
  'h6',        'html',
  'ul',        'ins',
  'noscript',  'object',
  'ol',        'optgroup',
  'p',         'script',
  'style',     'select',
  'table',     'tbody',
  'tfoot',     'thead',
]
for tag in BLOCK_TAGS:
    register_html_plugin(tag, is_block=True)


INLINE_TAGS = [
  'a',        'abbr',   'acronym', 'area',
  'b',        'base',   'bdo',     'big',
  'body',     'br',     'button',  'caption',
  'cite',     'code',   'col',     'colgroup',
  'del',      'dfn',    'em',      'fieldset',
  'form',     'i',      'ins',     'kbd',
  'label',    'legend', 'li',      'link',
  'map',      'option', 'param',   'pre',
  'q',        'samp',   'small',   'span',
  'strong',   'sub',    'sup',     'td',
  'textarea', 'th',     'title',   'tr',
  'tt',       'var',
]
for tag in INLINE_TAGS:
    register_html_plugin(tag, is_block=False)


SELF_CLOSING = [
    'hr',
    'img',
    'input',
    'meta',
]
for tag in SELF_CLOSING:
    register_html_plugin(tag, self_closing=True)
