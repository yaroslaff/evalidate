#!/usr/bin/env python3

import requests
from evalidate import Expr, ValidationException, CompilationException, ExecutionException
import json
import sys

data = requests.get('https://dummyjson.com/products?limit=100').json()

try:
    src = sys.argv[1]
except IndexError:
    src = 'True'

try:
    expr = Expr(src)
except (ValidationException, CompilationException) as e:
    print(e)
    sys.exit(1)

c=0
for p in data['products']:
    # print(p)
    try:
        r = expr.eval(p)
        if r:
            print(json.dumps(p, indent=2))
            c+=1
    except ExecutionException as e:
        print("Runtime exception:", e)
print("# {} products matches".format(c))
