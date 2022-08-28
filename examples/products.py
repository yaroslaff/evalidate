#!/usr/bin/env python3

import requests
from evalidate import evalidate, ValidationException, CompilationException
import json
import sys

data = requests.get('https://dummyjson.com/products?limit=100').json()

try:
    src = sys.argv[1]
except IndexError:
    src = 'True'

try:
    node = evalidate(src)
except (ValidationException, CompilationException) as e:
    print(e)
    sys.exit(1)


code = compile(node, '<user filter>', 'eval')

c=0
for p in data['products']:
    # print(p)
    try:
        r = eval(code, p.copy())
        if r:
            print(json.dumps(p, indent=2))
            c+=1
    except Exception as e:
        print("Runtime exception:", e)
print("# {} products matches".format(c))
