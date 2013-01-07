from plywood import plywood
# from pytest import raises


def simple_test():
    assert plywood("""
html
"""[1:-1]) == '<html></html>'


def simple_test2():
    assert plywood("""
html:
    head
    body:
        div
"""[1:-1]) == '<html><head></head><body><div></div></body></html>'
