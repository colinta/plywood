from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn(accepts_block=True)
def ieif(block, condition):
    opener = '<!--[if {0}]>\n'.format(condition)
    closer = '\n<![endif]-->'
    return opener + block(indent=True) + closer
