from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn('str')
def _str(*args, **kwargs):
    return str(*args, **kwargs)


@PlywoodEnv.register_fn('unicode')
def _unicode(*args, **kwargs):
    return unicode(*args, **kwargs)


@PlywoodEnv.register_fn('int')
def _int(*args, **kwargs):
    return int(*args, **kwargs)


@PlywoodEnv.register_fn('bool')
def _bool(*args, **kwargs):
    return bool(*args, **kwargs)


@PlywoodEnv.register_fn('float')
def _float(*args, **kwargs):
    return float(*args, **kwargs)


@PlywoodEnv.register_fn('list')
def _list(*args, **kwargs):
    return list(*args, **kwargs)


@PlywoodEnv.register_fn('dict')
def _dict(*args, **kwargs):
    return dict(*args, **kwargs)
