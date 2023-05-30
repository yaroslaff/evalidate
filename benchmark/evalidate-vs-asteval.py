#!/usr/bin/env python3

from asteval import Interpreter
import timeit
import evalidate
import requests

context = {'a':1, 'b': 2}
src="""a+b"""
node = evalidate.evalidate(src)
code = compile(node, '<usercode>', 'eval')


products = requests.get('https://dummyjson.com/products?limit=100').json()['products'] * 1000

# global asteval interpreter
gi = Interpreter()

gi.symtable = context

def test_asteval():
    aeval = Interpreter({**context}, minimal=True)
    result = aeval(src)

def test_asteval_reuse_interpreter():
    result = gi(src)


def test_asteval_products():
    aeval = Interpreter()
    src = """
counter=0
for p in products:
    if p['price']<20:
        counter += 1
counter
    """
    aeval.symtable['products'] = products

    result = aeval(src)

def test_evalidate():
    result = evalidate.safeeval(src, context)

def test_evalidate_compiled(code):
    result = eval(code)

def test_evalidate_products():
    src="""price < 20"""
    node = evalidate.evalidate(src)
    code = compile(node, '<usercode>', 'eval')
    counter = 0

    for p in products:
        if eval(code, p):
            counter+=1


def main():

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

    t = timeit.timeit('test_asteval_products()', setup='from __main__ import test_asteval_products, products', number=1)
    print(f"test_asteval_products() ({len(products)} items): {t:.3f}s")

    t = timeit.timeit('test_evalidate_products()', setup='from __main__ import test_evalidate_products, products', number=1)
    print(f"test_evalidate_products() ({len(products)} items): {t:.3f}s")


if __name__ == '__main__':
    main()