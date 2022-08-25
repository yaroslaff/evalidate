#!/usr/bin/env python3

from asteval import Interpreter
import timeit
import evalidate

context = {'a':1, 'b': 2}
src="""a+b"""

# global asteval interpreter
gi = Interpreter()

gi.symtable = context

def test_asteval():
    aeval = Interpreter({**context})
    result = aeval(src)

def test_asteval_reuse_interpreter():
    result = gi(src)

def test_evalidate():
    result = evalidate.safeeval(src, context)

def test_evalidate_compiled(code):
    result = eval(code)

node = evalidate.evalidate(src)
code = compile(node, '<usercode>', 'eval')

n = 100000

print("Src:", src)
print("Context:", context)
print("Runs:", n)

t = timeit.timeit('test_asteval()', setup='from __main__ import test_asteval', number=n)
print(f"asteval: {t:.3f}s")

t = timeit.timeit('test_asteval_reuse_interpreter()', setup='from __main__ import test_asteval_reuse_interpreter', number=n)
print(f"asteval (reuse interpreter): {t:.3f}s")


t = timeit.timeit('test_evalidate()', setup='from __main__ import test_evalidate', number=n)
print(f"safeeval: {t:.3f}s")

t = timeit.timeit('eval(code, context)', setup='from __main__ import code, context', number=n)
print(f"evalidate/compile/eval (reuse compiled code): {t:.3f}s")

