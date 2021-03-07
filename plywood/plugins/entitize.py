from plywood.env import PlywoodEnv
from plywood.util import entitize, deentitize

e = entitize

PlywoodEnv.register_fn()(e)
PlywoodEnv.register_fn()(entitize)
PlywoodEnv.register_fn()(deentitize)
