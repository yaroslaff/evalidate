# Evalidate
Evalidate is simple python module for safe and very fast eval()'uating user-supplied (possible malicious) python expressions.

## Upgrade warning
Version 2.0 is backward incompatible with older versions. `safeeval()` and `evalidate()` methods are removed, and EvalMode class is introduced.

See [upgrade example in ticket](https://github.com/yaroslaff/evalidate/issues/5) or use older (any before 2.0.0, e.g. [v1.1.0](https://pypi.org/project/evalidate/1.1.0/)) if you have old code and do not want to upgrade. But upgrading is easy, so please consider this option.

## Purpose
Originally it's developed for filtering complex data structures e.g. 

Find cheap smartphones available for sale:
```python
category=="smartphones" and price<300 and stock>0
```

But also, it can be used for other expressions, e.g. arithmetical, like
```python
a+b-100
```

Evalidate is fastest among all (known to me) secure eval python modules.

## Install

```shell
pip3 install evalidate
```
    
## Security

Built-in python features such as compile() or eval() are quite powerful to run any kind of user-supplied code, but could be insecure if used code is malicious like `os.system("rm -rf /")`. Evalidate works on whitelist principle, allowing code only if it consist only of safe operations (based on authors views about what is safe and what is not, your mileage may vary - but you can supply your list of safe operations)


## TL;DR. Just give me safe eval!
```python       
from evalidate import Expr, EvalException

src = 'a + 40 > b'
# src = "__import__('os').system('clear')"

try:
    print(Expr(src).eval({'a':10, 'b':42}))
except EvalException as e:
    print(e)
```

Gives output: `True`

In case of dangerous code (uncomment second src line to test):
  
output will be: `ERR: Operation type Call is not allowed`


## Exceptions
Evalidate throws exceptions `CompilationException`, `ValidationException`, `ExecutionException`. All of them
inherit from base exception class `EvalException`.

## Configure validation
Evalidate is very flexible, depending on security model, same code can either pass validation or raise exception.

EvalModel is security model class for eval - lists of allowed AST nodes, function calls, attributes and dict of imported functions. There is built-in model `base_eval_model` with basic operations allowed (which are safe from authors point of view).

You can create custom empty model (and extend it later):
~~~python
my_model = evalidate.EvalModel()
~~~

(nothing is allowed by default, even `1+2` will not be considered safe)

or you may start from `base_eval_mode` and extend it:
~~~python
from evalidate import Expr, base_eval_model

my_model = base_eval_model.clone()
my_model.nodes.append('Mult')

Expr('2*2', model=my_model).eval()
~~~

To enable `int()` function, need to allow `'Call'` node and add this function to list of allowed function:

~~~python
my_model.nodes.append('Call')
my_model.allowed_functions.append('int')

Expr('int(36.6)', model=my_model).eval()
~~~

Or, to call attributes:
~~~python
m = base_eval_model.clone()
m.nodes.extend(['Call', 'Attribute'])
m.attributes.append('startswith')

src = '"abcdef".startswith("abc")'
r = evalidate.Expr(src, model=m).eval()
~~~

But even with this settings, exploiting it with expression like `__builtins__["eval"](1)` will fail (good!).


### Exporting my functions to eval code
~~~python
def one():
  return 1

m = base_eval_model.clone()
m.nodes.append('Call')
m.imported_functions["one"] = one
Expr('one()', model=m).eval()
~~~

## Improve speed by using native eval() with validated code
Evalidate is very fast, but it's still takes CPU cycles... If you want to achieve maximal possible speed, you can use python native [eval](https://docs.python.org/3/library/functions.html#eval) with this kind of code:

~~~python
from evalidate import Expr

d = dict(a=1, b=2)
expr = Expr('a+b')
eval(expr.code, None, d) # <-- native python eval, will run at eval() speed
~~~

This is as secure as expr.eval(), because `expr.code` is already validated to be secure.

Difference is very little: execution of `expr.code` can throw any exception, while `expr.eval()` can throw only ExecutionException. Also, if you want to export your functions to eval, you should do this manually. 

## Limitations

evalidate uses [ast.parse()](https://docs.python.org/3/library/ast.html#ast.parse) to get [AST node](https://docs.python.org/3/library/ast.html#node-classes) to validate it.

>Warning
>
>It is possible to crash the Python interpreter with a sufficiently large/complex string due to stack depth limitations in Python’s AST compiler. 

In my test, works well with 200 nested int(): `int(int(.... int(1)...))` but not with 201. Source code is 1000+ characters. But even if evalidate will get such code, it will just raise `CompilationException`.


### evalidate.security.test_security()
Evalidate is very flexible and it's possible to shoot yourself in foot if you will try hard. `test_security()` checks your configuration (nodes, funcs, attrs) against given list of possible attack code or against built-in list of attacks. `test_security()` returns True if everything is OK (all attacks raised ValidationException) or False if something passed.

This code will never print (I hope).
~~~python
from evalidate.security import test_security

test_security() or print("default rules are vulnerable!")
~~~

But this will fail because nodes/funcs leads to successful validation for attack (suppose you do not want anyone to call `int()`)
~~~python
from evalidate.security import test_security

attacks = ['int(1)']

test_security(attacks, addnodes=['Call'], funcs=['int'], verbose=True)
~~~

It will print:
~~~
Testing attack code:
int(1)
Problem! Attack passed validation without exception!
Code:
int(1)
~~~




## Example

### Filtering by user-supplied condition ###

This is code of `examples/products.py`. Expression is validated and compiled once and executed (as byte-code, very fast) many times, so filtering is both fast and secure.


~~~python
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
~~~

~~~shell
# print all 100 products
./products.py

# Only cheap products, 8 matches
./products.py 'price<20'

# smartphones (5)
./products.py 'category=="smartphones"'

# good smartphones
./products.py 'category=="smartphones" and rating>4.5'

# cheap smartphones
./products.py 'category=="smartphones" and price<300'
~~~
                                       

## Similar projects and benchmark

[asteval](https://newville.github.io/asteval/)

While asteval can compute much more complex code (define functions, use python math libraries) it has drawbacks:
- asteval is much slower (evalidate can be used at speed of eval() python bytecode)
- user can provide source code which runs very long time and consumes many resources 


[simpleeval](https://github.com/danthedeckie/simpleeval)
Very similar project, using AST approach too and optimized to re-evaluate pre-parsed expressions. But parsed expressions are stored as more high-level [ast.Expr](https://docs.python.org/3/library/ast.html#ast.Expr) type and this approach is few times slower, while evalidate uses python native `code` type and evaluation itself goes at speed of python eval()

evalidate is good to run same expression against different data.

## Benchmarking
We use `benchmark/benchmark.py` in this repository.
We prepare list of 1 million of products (actually, we take just 100 products sample, but repeat it 10 000 times to get 1 million), and then filter it, finding only specific products on "untrusted user-supplied expression" (`price < 20` in this case)

~~~
Products: 1000000 items
evalidate_raw_eval(): 0.266s
evalidate_eval(): 0.326s
test_simpleeval(): 1.824s
test_asteval(): 26.106s
~~~

As you see, evalidate is few times faster then simpleeval and both are much faster then asteval.

Maybe my test is not perfectly optimized (I'm not expert with simpleeval/asteval), if you can suggest better filtering sample code (which produces faster result), I will include it. (Benchmark code must assume expression as unknown in advance and untrusted)


## Read about eval() risks

- https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
- https://netsec.expert/posts/breaking-python3-eval-protections/
- https://realpython.com/python-eval-function/

Note: realpython article shows example with nice short method of validation source (using `code.co_names`), 
but it's vulnerable, it passes "bomb" from Ned Batchelder article (bomb has empty `co_names` tuple) and crash interpreter. Evalidate can block this code and similar bombs (unless you will intentionally configure evalidate to pass specific bomb code. Yes, with evalidate it is hard to shoot yourself in the foot, but it is possible if you will try hard).

## More info

Want more info? Check source code of module, it's very short and simple, easy to modify

## Contact

Write me: yaroslaff at gmail.com
