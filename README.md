# Evalidate
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) logical expressions in python syntax.

## Purpose
Originally it's developed for filtering complex data structures e.g. 

Find cheap smartphones available for sale:
```python
category="smartphones" and price<300 and stock>0
```

But also, it can be used for other expressions, e.g. arithmetical, like
```python
a+b-100
```

Evalidate tries to be both secure and fast (when properly used).

## Install

```shell
pip3 install evalidate
```
    
## Security

Built-in python features such as compile() or eval() are quite powerful to run any kind of user-supplied code, but could be insecure if used code is malicious like `os.system("rm -rf /")`. Evalidate works on whitelist principle, allowing code only if it consist only of safe operations (based on authors views about what is safe and what is not, your mileage may vary - but you can supply your list of safe operations)


## TL;DR. Just give me safe eval!
```python       
from evalidate import safeeval, EvalException

src="a+b" # source code
# src="__import__('os').system('clear')"
c={'a': 1, 'b': 2} # context, variables which will be available for code

try:
    result = safeeval(src,c)
    print(result)
except EvalException as e:
    print("ERR:", e)
```

Gives output:

    3

In case of dangerous code:
```python
src="__import__('os').system('clear')"
```    
    
output will be: `ERR: Operation type Call is not allowed`


## Exceptions
Evalidate throws exceptions `CompilationException`, `ValidationException`, `ExecutionException`. All of them
inherit from base exception class `EvalException`.

## Configure validation
Evalidate is very flexible, depending on parameters, same code can either pass validation or raise exception.

### Safenodes and addnodes
Evalidate has built-in set of python operations, which are considered 'safe' (from author point of view). Code is considered valid only if all of it's operations are in this list. You can override this list by adding argument `safenodes` like:
```python
result = evalidate.safeeval(src, context, safenodes=['Expression','BinOp','Num','Add'])
```
this will be enough for `1+1` expression (in src argument), but not for `1-1`. If you will try '1-1', it will report error: `ERROR: Validation error: Operaton type Sub is not allowed`

This way you can start from scratch and allow only required operations. As an alternative, you can use built-in list of allowed operations and extend it if needed, using `addnodes` argument.

For example, "1*1" will give error:

  ERROR: Validation error: Operaton type Mult is not allowed


But it will work with addnodes:
```python
result = evalidate.safeeval(src,c, addnodes=['Mult'])
```    
Please note, using 'Mult' operation isn't very secure, because for strings it can lead to Out-of-memory:
```python
src='"a"*1000000*1000000*1000000*1000000'
```    
and will raise runtime exception: `ERROR: Runtime error (OverflowError): repeated string is too long`

### Allowing function calls
Evalidate does not allow any function calls by default:
```python
>>> from evalidate import safeeval, EvalException
>>> try:
...   safeeval('int(1)')
... except EvalException as e:
...   print(e)
... 
Operation type Call is not allowed
```

To enable int() function, need to allow 'Call' node and  add this function to list of allowed function:
```python
>>> evalidate.safeeval('int(1)', addnodes=['Call'], funcs=['int'])
1
```
Attempt to call other functions will fail (because it's not in funcs list):
```python
evalidate.safeeval('1+round(2)', addnodes=['Call'], funcs=['int'])
```
This will throw `ValidationException`.

Attributes calls (`"aaa".startswith("a")`) could be allowed (with proper `addnodes` and `attrs`) but
other indirect function calls (like: `__builtins__['eval']("print(1)")`) are not allowed,


### Accessing attributes (attrs parameter); data as classes

If data represented as object with attributes (not as dictionary) we have to add 'Attribute' to safe nodes. Increase salary for person for 200, and additionaly 25 for each year (s)he works in company.

```python
from evalidate import safeeval, EvalException
                        
class Person:
    pass
                        
p = Person()
p.salary=1000
p.age=5
                        
data = {'p':p}
src = 'p.salary+200+p.age*25'
try:                        
    result = safeeval(src,data,addnodes=['Attribute','Mult'], attrs=['salary', 'age'])                        
    print("result", result)
except EvalException as e:
    print("ERR:",e)
```

### Calling attributes
This code will not work:
~~~python
safeeval('"abc".startswith("a")')
~~~
Because: `evalidate.ValidationException: Operation type Call is not allowed`

To make it working:
~~~python
print(safeeval('"abc".startswith("a")', addnodes=['Call', 'Attribute'], attrs=['startswith']))
~~~

## Functions

`safeeval()` is simplest possible replacement to `eval()`. It is good to evaluate something once or few times, where speed is not an issue. If you need to eval same code 2nd time, it will take same 'long' time to parse/validate code. 

`evalidate()` is just little more complex, but returns validated safe python AST node, which can be compiled to python bytecode, and executed at full speed. (And this code is safe after evalidate)

`security.test_security()` checks configuration(nodes, funcs, attrs) against set of attacks.


### evalidate.safeeval()

```python
result = safeeval(expression, context={}, safenodes=None, addnodes=None, funcs=None, attrs=None)
```

`safeeval` is higher-level wrapper of evalidate(), which validates code and runs it (if validation is successful). Throws exception if compilation(parsing), validation or execution fails.

`expression` - python expression like `salary+100` or `category="smartphones" and price<300 and stock>0`.

`context` - dictionary of variables, available for evaluated code.

`safenodes`, `addnodes`, `funcs` and `attrs` are same as in `evalidate()`

returns result of evaluation of expression. 

### evalidate.evalidate()     
```python
node = evalidate(expression, safenodes=None, addnodes=None, funcs=None, attrs=None)
```
`evalidate()` is main (and recommended to use) method, performs parsing of python expession, validates it, and returns python AST (Abstract Syntax Tree) structure, which can be later compiled and executed. Evalidate does not evaluates code, use `compile()` and `eval()` after `evalidate()`.


```python            

>>> import evalidate
>>> node = evalidate.evalidate('1+2')
>>> code = compile(node,'<usercode>','eval')
>>> eval(code)
3
```    
    
- `expression` - python expression `salary+100` or `category="smartphones" and price<300 and stock>0`.
- `safenodes` - list of allowed nodes. This will *override* built-in list of allowed nodes. e.g. `safenodes=['Expression','BinOp','Num','Add'])`
- `addnodes` - list of allowed nodes. This will *extend* built-in lsit of allowed nodes. e.g. `addnodes=['Mult']`
- `funcs` - list of allowed function calls. You need to add 'Call' to safe nodes. e.g. `funcs=['int']`
- `attrs` - list of allowed attributes. You need to add 'Attribute' to attrs. e.g. `attrs=['salary']`.

    
evalidate() throws `CompilationException` if cannot parse source code and `ValidationException` if it doesn't like source code (if code has unsafe operations).
    
Even if evalidate is successful, this doesn't guarantees that code will run well, For example, code still can have `NameError` (if tries to access undefined variable) or `ZeroDivisionError`.

evalidate uses [ast.parse()](https://docs.python.org/3/library/ast.html#ast.parse) and returns [AST node](https://docs.python.org/3/library/ast.html#node-classes).

>Warning
>
>It is possible to crash the Python interpreter with a sufficiently large/complex string due to stack depth limitations in Python’s AST compiler. 

In my test, works well with 200 nested int(): `int(int(.... int(1)...))` but not with 201. Source code is 1000+ characters. But even if evalidate will get such code, it will just raise `CompilationException`.


### evalidate.security.test_security()
Evalidate is very flexible and it's possible to shoot yourself in foot if you will try hard. `test_security()` checks your configuration (addnodes/safenodes, funcs, attrs) against given list of possible attack code or against built-in list of attacks. `test_security()` returns True if everything is OK (all attacks raised ValidationException) or False if something passed.

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
Very similar project, using AST approach too and optimized to re-evaluate pre-parsed expressions. But parsed expressions are stored as more high-level [ast.Expr](https://docs.python.org/3/library/ast.html#ast.Expr) type and this approach is ~10 times slower, while evalidate uses python native `code` type and evaluation itself goes at speed of python eval()


evalidate is good to run short same code against different data.

## Benchmarking
We use `evalidate-vs-asteval.py` which is in benchmark/ directory of repository.
We prepare list of 1 million of products (actually, we take just 100 products sample, but repeat it 10 000 times to get 1 million), and then filter it, finding only specific products on "untrusted user-supplied expression" (`price < 20` in this case)

~~~
Products: 1000000 items
test_asteval_products(): 25.920s
test_simpleeval_products(): 1.779s
test_evalidate_products(): 0.160s
~~~

As you see, evalidate is almost 10 times faster then simpleeval and both are much faster then asteval.

Maybe my test is not perfectly optimized (I'm not expert with simpleeval/asteval), if you can suggest better filtering sample code (which produces faster result), I will include it. But benchmark code must assume expression as unknown and untrusted.


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
