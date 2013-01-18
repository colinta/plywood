from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn('str')
def _str(val):
    return str(val)


@PlywoodEnv.register_fn('unicode')
def _unicode(val):
    return unicode(val)


@PlywoodEnv.register_fn('int')
def _int(val):
    return int(val)


@PlywoodEnv.register_fn('bool')
def _bool(val):
    return bool(val)


@PlywoodEnv.register_fn('float')
def _float(val):
    return float(val)
