#!/usr/bin/env python3

import requests
import evalidate
import json
import sys

data = requests.get('https://dummyjson.com/products?limit=100').json()

try:
    src = sys.argv[1]
except IndexError:
    src = 'True'

try:
    node = evalidate.evalidate(src)
except evalidate.ValidationException as e:
    print(e)
    sys.exit(1)

code = compile(node, '<user filter>', 'eval')

c=0
for p in data['products']:
    # print(p)
    r = eval(code, p.copy())
    if r:
        print(json.dumps(p, indent=2))
        c+=1
print("# {} products matches".format(c))
