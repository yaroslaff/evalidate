#!/usr/bin/env python3

from asteval import Interpreter
import timeit
import evalidate
import requests
import simpleeval

# context = {'a':1, 'b': 2}
# src="""a+b"""
# node = evalidate.evalidate(src)
# code = compile(node, '<usercode>', 'eval')

"""
    Our test: we prepare large list of products and filter it, find all items cheaper then 20
"""

mult = 10000

products = requests.get('https://dummyjson.com/products?limit=100').json()['products'] * mult
accurate_counter = 8 * mult


# gi.symtable = context

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
    assert(result == accurate_counter)

def test_simpleeval_products():
    code = """price < 20"""

    s = simpleeval.SimpleEval()
    parsed = s.parse(code)

    counter = 0

    for p in products:
        s.names = p
        if s.eval(code, previously_parsed=parsed, ):
            counter += 1
    assert(counter == accurate_counter)


def test_evalidate_products():
    src="""price < 20"""
    node = evalidate.evalidate(src)
    code = compile(node, '<usercode>', 'eval')
    counter = 0

    for p in products:
        if eval(code, p):
            counter+=1
    assert(counter == accurate_counter)

def main():

    print(f"Products: {len(products)} items")

    t = timeit.timeit('test_asteval_products()', setup='from __main__ import test_asteval_products, products', number=1)
    print(f"test_asteval_products(): {t:.3f}s")

    t = timeit.timeit('test_simpleeval_products()', setup='from __main__ import test_simpleeval_products, products', number=1)
    print(f"test_simpleeval_products(): {t:.3f}s")

    t = timeit.timeit('test_evalidate_products()', setup='from __main__ import test_evalidate_products, products', number=1)
    print(f"test_evalidate_products(): {t:.3f}s")


if __name__ == '__main__':
    main()