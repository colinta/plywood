'''
``extends`` and ``block``
~~~~~~~~~~~~~~~~~~~~~~~~~

``extends`` is used to import a layout.  That layout must contain ``block``
commands that the template can provide, or a ``yield`` statement that outputs
the block passed to ``extends``.  A ``block`` command stores a section of
html, but only the first time the block is defined.  The ``extends`` body is
executed *first*, and so blocks defined in the body of the extends method
override default block content defined in the layout.

Example::

    # template.ply
    extends 'layout':
        block 'head':
            entitize '<head> content'
        block 'head':
            'this content is ignored'
        'main content'  # this will be output from the yield method

    # layout.ply
    html:
        head:
            block 'head'  # this will be a get_block request
            block 'extrahead':
                'default content, which can be ignored'
        body:
            yield

When a layout is extended, it will replace the block command to an internal one
that outputs the stored blocks.  This function is available as
``get_block(name)``.  You can use this to re-use some content::

    block 'hr':
        div.hr
    html:
        body:
            get_block 'hr'
            p 'some content'
            get_block 'hr'

This is an unusual usage of ``block``, but there it is.

Another interesting use of blocks is in AJAX requests. It is sometimes the case
that you will want a template to render only *part* of its output when the
request is coming in via ajax.  In this case, you will want to perform a
conditional ``extends``::

    # template.ply
    # define the block first - this will not output anything
    block 'yield':
        p 'this is the page content'

    if request.is_xhr:
        # for an ajax request we output the content
        get_block 'yield'
    else:
        # otherwise we use the layout, which will pick up on the ``block``
        # defined above.
        extends 'layout'

Lastly, a block can extend another block, which is useful if you want to define
some append or prepend content to a block::

    # layout.ply
    nav: ul:
        block 'nav':
            links = [{'href':'/link-one',title:'Link One'}]
            for link in links:
                li: a href=link.href: link.title
    # <nav><ul>
    #   <li><a href="/link-one">Link One</a></li>
    # </ul></nav>

    # template.ply
    extends 'layout':
        block 'nav':
            super
            li: a href='/another': 'Another'
    # <nav><ul>
    #   <li><a href="/link-one">Link One</a></li>
    #   <li><a href="/another">Another</a></li>
    # </ul></nav>
'''
from plywood.env import PlywoodEnv
from plywood.exceptions import InvalidArguments
from plywood.values import PlywoodBlock
from .include import include


@PlywoodEnv.register_runtime()
def extends(states, scope, arguments, block):
    if not len(arguments.args):
        raise InvalidArguments('A layout name is required in `extends`')
    if len(arguments.args) != 1:
        raise InvalidArguments('`extends` only accepts one argument')

    scope.push()
    yield_content = block.get_value(scope)  # executes the body, to define blocks
    scope['__yield'] = yield_content  # makes the extends body available to the yield method

    # inside the extended layout, block => get_block
    scope['block'] = scope['get_block']

    # include the layout
    states, retval = include(states, scope, arguments, PlywoodBlock(block.location, []))
    scope.pop()
    return states, retval


@PlywoodEnv.register_runtime('block')
def define_block(states, scope, arguments, block):
    if not len(arguments.args):
        raise InvalidArguments('A block name is required in `block`')
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise InvalidArguments('`block` only accepts one argument')
    block_name = arguments.args[0].python_value(scope)
    scope['__blocks'][block_name] = block
    return states, ''


@PlywoodEnv.register_runtime()
def get_block(states, scope, arguments, block):
    if not len(arguments.args):
        raise InvalidArguments('A block name is required in `get_block`')
    if len(arguments.args) != 1 or len(arguments.kwargs):
        raise InvalidArguments('`get_block` only accepts one argument')
    # if a block is defined, it will be stored as the default
    block_name = arguments.args[0].python_value(scope)
    if block.lines:
        if block_name in scope['__blocks']:
            scope.push()
            scope['super'] = block.get_value(scope)
            scope['super'].suppress_nl = True
            retval = scope['__blocks'][block_name].get_value(scope)
            scope.pop()
        else:
            retval = block.get_value(scope)
    else:
        retval = scope['__blocks'][block_name].get_value(scope)
    return states, retval


@PlywoodEnv.register_runtime('yield')
def _yield(states, scope, arguments, block):
    if len(arguments.args) or len(arguments.kwargs) or len(block.lines):
        raise InvalidArguments('`yield` does not accept any argumentsor block')
    yield_content = scope.get('__yield', '')
    return states, yield_content


@PlywoodEnv.register_startup()
def startup(plywood, scope):
    scope['__blocks'] = {}
