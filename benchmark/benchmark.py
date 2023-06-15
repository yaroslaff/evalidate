#!/usr/bin/env python3

from asteval import Interpreter
import timeit
import evalidate
import requests
import simpleeval
import json
from pprint import pprint

# context = {'a':1, 'b': 2}
# src="""a+b"""
# node = evalidate.evalidate(src)
# code = compile(node, '<usercode>', 'eval')

"""
    Our test: we prepare large list of products and filter it, find all items cheaper then 20
"""

mult = 10000
# mult = 1

products = requests.get('https://dummyjson.com/products?limit=100').json()['products'] * mult
accurate_counter = 8 * mult


# gi.symtable = context

def test_asteval():
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
    assert(result == accurate_counter)

def test_simpleeval():
    code = """price < 20"""

    s = simpleeval.SimpleEval()
    parsed = s.parse(code)

    counter = 0

    for p in products:
        s.names = p
        if s.eval(code, previously_parsed=parsed, ):
            counter += 1
    assert(counter == accurate_counter)

def evalidate_raw_eval():
    src="""price < 20"""
    e = evalidate.Expr(src)
    counter = 0

    for p in products:
        if eval(e.code, None, p):
            counter+=1
    assert(counter == accurate_counter)

def evalidate_eval():
    src="""price < 20"""
    e = evalidate.Expr(src)
    counter = 0

    for p in products:
        if e.eval(p):
            counter+=1

    assert(counter == accurate_counter)


def main():

    print(f"Products: {len(products)} items")


    t = timeit.timeit('evalidate_raw_eval()', setup='from __main__ import evalidate_raw_eval, products', number=1)
    print(f"evalidate_raw_eval(): {t:.3f}s")

    t = timeit.timeit('evalidate_eval()', setup='from __main__ import evalidate_eval, products', number=1)
    print(f"evalidate_eval(): {t:.3f}s")

    t = timeit.timeit('test_simpleeval()', setup='from __main__ import test_simpleeval, products', number=1)
    print(f"test_simpleeval(): {t:.3f}s")

    t = timeit.timeit('test_asteval()', setup='from __main__ import test_asteval, products', number=1)
    print(f"test_asteval(): {t:.3f}s")


if __name__ == '__main__':
    main()