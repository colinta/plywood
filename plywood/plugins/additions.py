from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn()
def reverse(contents):
    return contents[::-1]


@PlywoodEnv.register_fn()
def cdata(contents):
    return '<![CDATA[' + unicode(contents) + ']]>'
