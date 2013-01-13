'''
Any plugin that wants to support the ``break`` and ``continue`` clauses can
import them from here and add ``try/catch`` blocks that catch ``BreakException``
and ``ContinueException`` and use ``break`` and ``continue`` in their python
code.
'''
from plywood.values import PlywoodValue
from plywood.exceptions import BreakException, ContinueException


@PlywoodValue.register_fn('break')
def _break():
    raise BreakException()


@PlywoodValue.register_fn('continue')
def _continue():
    raise ContinueException()
