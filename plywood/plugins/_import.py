'''
You can import values into scope using this plugin::

    import os
    os.getcwd()
    os.getcwd  # when
'''
from plywood.values import PlywoodVariable, PlywoodParens, PlywoodOperator
from plywood.env import PlywoodEnv
# from plywood.runtime import Runtime, Continue
from plywood.exceptions import InvalidArguments


def join_module_names(token, scope_name=None):
    if isinstance(token, PlywoodOperator) and token.operator == '.':
        if scope_name is None:
            scope_name = token.left.get_name()
        return scope_name, token.left.get_name() + '.' + join_module_names(token.right, scope_name)[1]
    if not isinstance(token, PlywoodVariable):
        raise InvalidArguments('Only variable names are allowed in an import statement')
    if scope_name is None:
        scope_name = token.get_name()
    return scope_name, token.get_name()


@PlywoodEnv.register_runtime('import')
def _import(states, scope, arguments, block):
    if len(arguments.kwargs):
        raise InvalidArguments('`import` does not accept keyword arguments')
    if len(block.lines):
        raise InvalidArguments('`import` does not accept a block')
    for arg in arguments.args:
        scope_name, import_name = join_module_names(arg)
        scope[scope_name] = __import__(import_name)
    return states, ''


@PlywoodEnv.register_runtime('open')
def _open(states, scope, arguments, block):
    if len(block.lines):
        raise InvalidArguments('`import` does not accept a block')
    args = map(lambda arg: arg.python_value(scope), arguments.args)
    retval = open(*args)
    return states, retval

@PlywoodEnv.register_runtime('from')
def _from(states, scope, arguments, block):
    if len(arguments.kwargs):
        raise InvalidArguments('`from` does not accept keyword arguments')
    if len(block.lines):
        raise InvalidArguments('`from` does not accept a block')
    if len(arguments.args) != 2:
        raise InvalidArguments('`from` only accepts a module and a list of attributes to import')
    _, target = join_module_names(arguments.args[0])
    imports = arguments.args[1]
    if len(imports.args) == 1 and isinstance(imports.args[0], PlywoodParens):
        imports = imports.args[0]
    module = __import__(target)
    for var in imports.args:
        attr = var.get_name()
        scope[attr] = getattr(module, attr)
    return states, ''
