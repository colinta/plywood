from plywood.env import PlywoodEnv
from plywood.util import entitize, deentitize


PlywoodEnv.register_fn()(entitize)
PlywoodEnv.register_fn()(deentitize)
