from plywood import Plywood
print repr(Plywood('foo').run())
print repr(Plywood('"foo"').run())
print repr(Plywood('1').run())
print repr(Plywood('-1').run())
print repr(Plywood('0.123').run())
print repr(Plywood('-0.123').run())
print repr(Plywood('0x1e32').run())
print repr(Plywood('0o07126').run())
print repr(Plywood('0b010101').run())
print repr(Plywood('-0x1e32').run())

print repr(Plywood('foo + bar').run())
print repr(Plywood('foo - bar').run())
print repr(Plywood('foo * bar').run())
print repr(Plywood('foo / bar').run())
print repr(Plywood('foo * bar').run())
print repr(Plywood('foo % bar').run())
print repr(Plywood('foo / bar').run())
print repr(Plywood('foo . bar').run())
print repr(Plywood('foo = bar = foo + 1').run())
print repr(Plywood('foo(bar)').run())
print repr(Plywood('foo(bar, 1, key="value")').run())
print repr(Plywood('{foo: bar}').run())
print repr(Plywood('{"foo": "bar"}').run())
print repr(Plywood("foo\nbar").run())
print repr(Plywood("""
foo
"foo"
1
123
bar
foo(bar, item='value')
""").run())
