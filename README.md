Evalidate
===
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) logical expressions in python syntax.

Purpose
---
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

Install
---
```shell
pip install evalidate
```
    
Security
---
Built-in python features such as compile() or eval() is quite powerful to run any kind of user-supplied code, but could be insecure if used code is malicious like os.system("rm -rf /"). Evalidate works on whitelist principle, allowing code only if it consist only  of safe operations (based on authors views about what is safe and what is not, your mileage may vary - but you can supply your list of safe operations)

Very basic example
---
```python
import evalidate

src="a+b" # source code
c={'a': 1, 'b': 2} # context, variables which will be available for code

success,result = evalidate.safeeval(src,c)
if success:
    print result
else:
    print "ERROR:",result
```

Gives output:

    3

In case of dangerous code:
```python
src="__import__('os').system('clear')"
```    
    
output will be:

    ERROR: Validation error: Operaton type Call is not allowed
    
# Extending evalidate, safenodes and addnodes #
Evalidate has built-in set of python operations, which are considered 'safe' (from author point of view). Code is considered valid only if all of it's operations are in this lisst. You can override this list by adding argument *safenodes* like:
```python
success,result = evalidate.safeeval(src,c, safenodes=['Expression','BinOp','Num','Add'])
```
this will be enough for '1+1' expression (in src argument), but not for '1-1'. If you will try '1-1', it will report error:

    ERROR: Validation error: Operaton type Sub is not allowed


This way you can start from scratch and allow only required operations. As an alternative, you can use built-in list of allowed operations and extend it if needed, using *addnodes* argument.

For example, "1*1" will give error:

  ERROR: Validation error: Operaton type Mult is not allowed


But it will work with addnodes:
```python
success,result = evalidate.safeeval(src,c, addnodes=['Mult'])
```    
Please note, using 'Mult' operation isn't very secure, because for strings it can lead to Out-of-memory:
```python
src='"a"=="a"*100*100*100*100*100'
```    
    ERROR: Runtime error (OverflowError): repeated string is too long

# Allowing function calls
Evalidate does not allows any function calls by default:
```
>>> import evalidate
>>> evalidate.safeeval('1+int(2)')
(False, 'Validation error: Operaton type Call is not allowed')
```
To enable int() function, need to allow 'Call' node and  add this function to list of allowed function:
```
>>> evalidate.safeeval('1+int(2)', addnodes=['Call'], funcs=['int'])
(True, 3)
```
Attempt to call other functions will fail (because it's not in funcs list):
```
>>> evalidate.safeeval('1+round(2)', addnodes=['Call'], funcs=['int'])
(False, 'Validation error: Call to function round() is not allowed')
```

Functions
---

### safeeval()

```python
success,result = safeeval(src,context={}, safenodes=None, addnodes=None, funcs=None, attrs=None)
```

*safeeval* is C-style higher-level wrapper of evalidate(), which validates code and runs it (if validation is successful)

*src* - source expression like "person['Age']>30 and salary==10000"

*context* - dictionary of variables, available for evaluated code.

*safenodes*, *addnodes*, *funcs* and *attrs* are same as in evalidate()

return values:

*success* - binary, True if validation is successul and evaluation didn't thrown any exceptions. (False in this case) 

*result* - if success==True, result is result of expression. If success==False, result is string with error message, like "ERROR: Runtime error (NameError): name 'aaa' is not defined"
    
safeeval doesn't throws any exceptions

### evalidate()     
```python
node = evalidate(expression, safenodes=None, addnodes=None, funcs=None, attrs=None)
```
evalidate() is main (and recommended to use) method, performs parsing of python expession, validates it, and returns python AST (Abstract Syntax Tree) structure, which can be later compiled and executed
```python            

>>> import evalidate
>>> node = evalidate.evalidate('1+2')
>>> code = compile(node,'<usercode>','eval')
>>> eval(code)
3
```    
    
- *expression* - string with python expressions like '1+2' or 'a+b' or 'a if a>0 else b' or 'p.salary * 1.2'
- *safenodes* - list of allowed nodes. This will *override* built-in list of allowed nodes. e.g. `safenodes=['Expression','BinOp','Num','Add'])`
- *addnodes* - list of allowed nodes. This will *extend* built-in lsit of allowed nodes. e.g. `addnodes=['Mult']`
- *funcs* - list of allowed function calls. You need to add 'Call' to safe nodes. e.g. `funcs=['int']`
- *attrs* - list of allowed attributes. You need to add 'Attribute' to attrs. e.g. `attrs=['salary']`.

    
evalidate() throws ValueError if it doesn't like source code (if code has unsafe operations).
    
Even if evalidate is successful, this doesn't guarantees that code will run well, For example, code still can have NameError (if tries to access undefined variable) or ZeroDivisionError.

Examples
---

### Filtering by user-supplied condition ###
```python
import evalidate
    
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
    success, result = evalidate.safeeval(src,book)
    
    if success:
        if result:
            print book
    else:
        print "ERR:", result
```    
    
With first src line ('stock==0') it gives:

    {'price': 9.8, 'book': 'Gone Girl', 'stock': 0}

With second src line ('stock>0 and price>8') it gives:

    {'price': 12, 'book': 'Sirens of Titan', 'stock': 4}
    {'price': 14, 'book': 'Choke', 'stock': 2}
    


### Data as objects ###
Data represented as object with attributes (not as dictionary) (we have to add 'Attribute' to safe nodes). Increase salary for person for 200, and additionaly 25 for each year (s)he works in company.
```python
import evalidate
                        
class Person:
    pass
                        
p = Person()
p.salary=1000
p.age=5
                        
data = {'p':p}
src = 'p.salary+200+p.age*25'
                        
success, result = evalidate.safeeval(src,data,addnodes=['Attribute','Mult'], attrs=['salary', 'age'])
                        
if success:
    print "result", result
else:
    print "ERR:", result
```
                                                
### Validate, compile and evaluate code ###
```python
import evalidate
import os
    
data={'one':1,'two':2}
src='one+two+3'
#src='one+two+3+os.system("clear")'
    
try:
    node = evalidate.evalidate(src)
    code = compile(node,'<usercode>','eval')
    result = eval(code,{},data)
    print "result:",result
except ValueError:
    print "Bad source code:", src
```    
             
More info
---
Want more info? Check source code of module, it's very short and simple, easy to modify

Contact
---
Write me: yaroslaff@gmail.com
