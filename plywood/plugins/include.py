'''
Includes content from another template.  If you assign any keyword arguments,
those will be available in the scope of that template.
'''
import os

from plywood import Plywood
from plywood.values import PlywoodValue
from plywood.exceptions import InvalidArguments
from plywood.env import PlywoodEnv


@PlywoodEnv.register_runtime()
def include(states, scope, arguments, block):
    if len(arguments.args) != 1:
        raise InvalidArguments('`include` only accepts one argument')
    if len(block.lines):
        raise InvalidArguments('`include` does not accept a block')

    restore_scope = {}
    delete_scope = []
    if isinstance(scope['self'], PlywoodValue):
        context = scope['self'].python_value(scope)
    else:
        context = scope['self']

    if len(arguments.kwargs):
        kwargs = dict(
            (item.key.get_name(), item.value)
                for item in arguments.kwargs
                )
        for key, value in kwargs.items():
            if key in context:
                restore_scope[key] = context[key]
            else:
                delete_scope.append(key)
            context[key] = value

    if '__env' in scope:
        env = scope['__env']
    else:
        env = PlywoodEnv({'separator': ' '})

    template_name = arguments.args[0].python_value(scope)
    plywood = None
    for path in scope['__paths']:
        template_path = os.path.join(path, template_name) + '.ply'
        if template_path in env.includes:
            plywood = env.includes[template_path]
        elif os.path.exists(template_path):
            retval = ''
            with open(template_path) as f:
                input = f.read()
                plywood = Plywood(input)
                env.includes[template_path] = plywood
                # scope is not pushed/popped - `include` adds its variables to the local scope.

        if plywood:
            break

    if not plywood:
        raise Exception('Could not find template: {0!r}'.format(template_name))

    retval = plywood.run(context, env)

    if len(arguments.kwargs):
        for key, value in restore_scope.items():
            context[key] = value
        for key in delete_scope:
            del context[key]
    return states, retval


@PlywoodEnv.register_startup()
def startup(plywood, scope):
    if plywood.options.get('paths'):
        scope['__paths'] = plywood.options.get('paths')
    elif plywood.options.get('path'):
        scope['__paths'] = [plywood.options.get('path')]
    else:
        scope['__paths'] = [os.getcwd()]
