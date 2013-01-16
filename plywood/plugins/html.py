from plywood.env import PlywoodEnv
from plywood.element import output_element


def register_html_plugin(tag_name, is_self_closing=False):
    @PlywoodEnv.register_html_plugin(tag_name)
    def plugin(scope, arguments, block, classes):
        return output_element(scope, arguments, block, tag_name, classes, is_self_closing)
    plugin.__name__ = tag_name


from tags import BLOCK_TAGS, INLINE_TAGS, SELF_CLOSING

for tag in BLOCK_TAGS:
    register_html_plugin(tag)

for tag in INLINE_TAGS:
    register_html_plugin(tag)

for tag in SELF_CLOSING:
    register_html_plugin(tag, is_self_closing=True)
