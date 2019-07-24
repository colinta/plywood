from plywood.env import PlywoodEnv
from plywood.exceptions import InvalidArguments
from plywood.values import PlywoodBlock
from plywood.runtime import Continue
import misaka
import re


slug_remove = re.compile('\W+')

def sluggify(s):
    s = s.lower()
    return slug_remove.sub('-', s).strip('-')


class HeaderRenderer(misaka.HtmlRenderer):
    def header(self, header, n):
        header = header.strip()
        slug = sluggify(header)
        return "\n<h{n} id=\"{slug}\">{header}</h{n}>\n".format(**locals())


class PygmentsRenderer(misaka.HtmlRenderer):
    def block_code(self, text, lang):
        # pygments code highlighting
        if lang is None:
            return u'<pre><code>{}</pre></code>'.format(text)
        return p.highlight(text, get_lexer_by_name(lang), HtmlFormatter(cssclass='codehilite'))


class MyRenderer(HeaderRenderer, PygmentsRenderer):
    pass

renderer = MyRenderer()
compiler = misaka.Markdown(renderer,
    extensions=(
        misaka.EXT_FENCED_CODE, misaka.EXT_NO_INTRA_EMPHASIS,
        misaka.EXT_STRIKETHROUGH, misaka.EXT_SUPERSCRIPT,
        misaka.EXT_TABLES
        )
    )

@PlywoodEnv.register_runtime()
def markdown(states, scope, arguments, block):
    code = block.get_value(scope).python_value(scope)
    markup = misaka.smartypants(compiler(code).strip())
    return [Continue()], markup
