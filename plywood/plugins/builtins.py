from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn('round')
def _round(*args, **kwargs):
    return round(*args, **kwargs)
