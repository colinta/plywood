'''
Any plugin that wants to support the ``break`` and ``continue`` clauses can
import them from here and add ``try/catch`` blocks that catch ``BreakException``
and ``ContinueException`` and use ``break`` and ``continue`` in their python
code.
'''
from plywood.env import PlywoodEnv
from plywood.exceptions import BreakException, ContinueException


@PlywoodEnv.register_fn('break')
def _break():
    raise BreakException()


@PlywoodEnv.register_fn('continue')
def _continue():
    raise ContinueException()
