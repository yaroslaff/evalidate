# Evalidate
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) logical expressions in python syntax.

## Purpose
Originally it's developed for filtering (performing boolean expressions) complex data structures e.g. raise salary if 

```python
person.age>30 and person.salary>5000 or "Jack" in person.children
```
or, like simple firewall, allow inbound traffic if:

```python
(packet.tcp.dstport==22 or packet.tcp.dstport==80) and packet.tcp.srcip in WhiteListIP
```
But also, it can be used for other expressions, e.g. arithmetical, like
```python
a+b-100
```

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

## Extending evalidate: safenodes and addnodes
Evalidate has built-in set of python operations, which are considered 'safe' (from author point of view). Code is considered valid only if all of it's operations are in this list. You can override this list by adding argument `safenodes` like:
```python
result = evalidate.safeeval(src,c, safenodes=['Expression','BinOp','Num','Add'])
```
this will be enough for '1+1' expression (in src argument), but not for '1-1'. If you will try '1-1', it will report error:

    ERROR: Validation error: Operaton type Sub is not allowed


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
    ERROR: Runtime error (OverflowError): repeated string is too long

## Allowing function calls
Evalidate does not allow any function calls by default:
```
>>> from evalidate import safeeval, EvalException
>>> try:
...   safeeval('int(1)')
... except EvalException as e:
...   print(e)
... 
Operation type Call is not allowed
```

To enable int() function, need to allow 'Call' node and  add this function to list of allowed function:
```
>>> evalidate.safeeval('int(1)', addnodes=['Call'], funcs=['int'])
1
```
Attempt to call other functions will fail (because it's not in funcs list):
```
evalidate.safeeval('1+round(2)', addnodes=['Call'], funcs=['int'])
```
This will throw `ValidationException`.

Any indirect function calls (like: `__builtins__['eval']("print(1)")`) are not allowed. 


## Functions

There are two functions, `safeeval()` and `evalidate()`. 

`safeeval()` is simplest possible replacement to `eval()`. It is good to evaluate something once or few times, where speed is not an issue. If you need to eval same code 2nd time, it will take same 'long' time to parse/validate code. 

`evalidate()` is just little more complex, but returns validated safe python AST node, which can be compiled to python bytecode, and executed at full speed. (But this code is safe after evalidate)


### safeeval()

```python
result = safeeval(src, context={}, safenodes=None, addnodes=None, funcs=None, attrs=None)
```

`safeeval` is higher-level wrapper of evalidate(), which validates code and runs it (if validation is successful). Throws exception if compilation(parsing), validation or execution fails.

`src` - source expression like "person['Age']>30 and salary==10000"

`context` - dictionary of variables, available for evaluated code.

`safenodes`, `addnodes`, `funcs` and `attrs` are same as in `evalidate()`

returns result of evaluation of expression. 

### evalidate()     
```python
node = evalidate(expression, safenodes=None, addnodes=None, funcs=None, attrs=None)
```
`evalidate()` is main (and recommended to use) method, performs parsing of python expession, validates it, and returns python AST (Abstract Syntax Tree) structure, which can be later compiled and executed
```python            

>>> import evalidate
>>> node = evalidate.evalidate('1+2')
>>> code = compile(node,'<usercode>','eval')
>>> eval(code)
3
```    
    
- `expression` - string with python expressions like '1+2' or 'a+b' or 'a if a>0 else b' or 'p.salary * 1.2'
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


## Examples

### Filtering by user-supplied condition ###
```python
from evalidate import safeeval, EvalException
    
depot = [
    {
        'book': 'Sirens of Titan',
        'price': 12,
        'stock': 4
    },
    {
        'book': 'Gone Girl',
        'price': 9.8,
        'stock': 0
    },
    {
        'book': 'Choke',
        'price': 14,
        'stock': 2
    },
    {
        'book': 'Pulp',
        'price': 7.45,
        'stock': 4
    }
]
    
#src='stock==0' # books out of stock
src='stock>0 and price>8' # expensive book available for sale
    
for book in depot:
    try:
        result = safeeval(src,book)
        if result:
            print(book)
    except EvalException as e:
        print("ERR:", e)
```    
    
With first src line ('stock==0') it gives:

    {'price': 9.8, 'book': 'Gone Girl', 'stock': 0}

With second src line ('stock>0 and price>8') it gives:

    {'price': 12, 'book': 'Sirens of Titan', 'stock': 4}
    {'price': 14, 'book': 'Choke', 'stock': 2}
    


### Data as objects
Data represented as object with attributes (not as dictionary) (we have to add 'Attribute' to safe nodes). Increase salary for person for 200, and additionaly 25 for each year (s)he works in company.
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
                                                
### Validate, compile and evaluate code
```python
import evalidate

def test(src):   
    data={'one':1,'two':2}

    try:
        node = evalidate.evalidate(src)
    except evalidate.CompilationException:
        print("Bad source code:", repr(src))
        return
    except evalidate.ValidationException:
        print("Dangerous code:", repr(src))
        return

    code = compile(node,'<usercode>','eval')
    try:
        result = eval(code,{},data)
        print("result:", result)
    except Exception as e:
        # almost any kind of exception can happen here
        print("Runtime exception:",e)

srclist=['one+two+3', 'one+two+3+os.system("clear")', '', '1/0']

for src in srclist:
    test(src)    
```    
             
Similar projects
---
[asteval](https://newville.github.io/asteval/)

Read about eval() risks
---
- https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
- https://netsec.expert/posts/breaking-python3-eval-protections/

More info
---
Want more info? Check source code of module, it's very short and simple, easy to modify

Contact
---
Write me: yaroslaff at gmail.com
