﻿# About Evalidate
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) logical expressions in python syntax.

# Purpose
Originally it's developed for filtering (performing boolean expressions) complex data structures e.g. raise salary if 

    person.age>30 and person.salary>5000 or "Jack" in person.children

or, like simple firewall, allow inbound traffic if:

    (packet.tcp.dstport==22 or packet.tcp.dstport==80) and packet.tcp.srcip in WhiteListIP

But also, it can be used for other expressions, e.g. arithmetical, like
    a+b-100
    

# Install
    pip install evalidate
    
# Security
Built-in python features such as compile() or eval() is quite powerful to run any kind of user-supplied code, but could be insecure if used code is malicious like os.system("rm -rf /"). Evalidate works on whitelist principle, allowing code only if it consist only  of safe operations (based on authors views about what is safe and what is not, your mileage may vary - but you can supply your list of safe operations)

# Examples
    import evalidate

    src="a+b" # source code
    c={'a': 1, 'b': 2} # context, variables which will be available for code

    success,result = evalidate.safeeval(src,c)
    if success:
        print result
    else:
        print "ERROR:",result


Gives output:

    3

In case of dangerous code:
    
    src="__import__('os').system('clear')"
    
    
output will be:

    ERROR: Validation error: Operaton type Call is not allowed
    
# Extending evalidate, safenodes and addnodes
Evalidate has built-in set of python operations, which are considered 'safe' (from author point of view). Code is considered valid only if all of it's operations are in this list. You can override this list by adding argument *safenodes* like:
    
    success,result = evalidate.safeeval(src,c, safenodes=['Expression','BinOp','Num','Add'])

this will be enough for '1+1' expression (in src argument), but not for '1-1'. If you will try '1-1', it will report error:

    ERROR: Validation error: Operaton type Sub is not allowed


This way you can start from scratch and allow only required operations. As an alternative, you can use built-in list of allowed operations and extend it if needed, using *addnodes* argument.

For example, "1*1" will give error:

  ERROR: Validation error: Operaton type Mult is not allowed


But it will work with addnodes:

    success,result = evalidate.safeeval(src,c, addnodes=['Mult'])
    
Please note, using 'Mult' operation isn't very secure, because for strings it can lead to Out-of-memory:

    src='"a"=="a"*100*100*100*100*100'
    
    ERROR: Runtime error (OverflowError): repeated string is too long
    
# Functions

## success,result = safeeval(src,context={}, safenodes=None, addnodes=None)

*safeeval* - is higher-level function of module, which validates code and runs it (if validation is successful)

*src* - source expression like "person['Age']>30 and salary==10000"

*context* - dictionary of variables, available for evaluated code.

return values:

*success* - binary, True if validation is successul and evaluation didn't thrown any exceptions. (False in this case) 

*result* - if success==True, result is result of expression. If success==False, result is string with error message, like "ERROR: Runtime error (NameError): name 'aaa' is not defined"
    
safeeval doesn't throws any exceptions    
    
## node = evalidate(expression,safenodes=None,addnodes=None)
evalidate() performs parsing of python expession, validates it, and returns python AST (Abstract Syntax Tree) structure, which can be later compiled and executed

    code = compile(node,'<usercode>','eval')
    eval(code)
    
    
evalidate() throws ValueError if it doesn't like source code (if it has unsafe operations).
    
Even if evalidate is successful, this doesn't guarantees that code will run well, For example, code still can have NameError (if tries to access undefined variable) or ZeroDivisionError.

# Examples

## Filtering by user-supplied condition:
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
    
    
With first src line ('stock==0') it gives:

    {'price': 9.8, 'book': 'Gone Girl', 'stock': 0}

With second src line ('stock>0 and price>8') it gives:

    {'price': 12, 'book': 'Sirens of Titan', 'stock': 4}
    {'price': 14, 'book': 'Choke', 'stock': 2}
    


## Data as objects
Data represented as object with attributes (not as dictionary) (we have to add 'Attribute' to safe nodes). Increase salary for person for 200, and additionaly 25 for each year (s)he works in company.

    import evalidate
                        
    class person:
        pass
                        
    p = person
    p.salary=1000
    p.age=5
                        
    data = {'p':p}
    src = 'p.salary+200+p.age*25'
                        
    success, result = evalidate.safeeval(src,data,addnodes=['Attribute','Mult'])
                        
    if success:
        print "result", result
    else:
        print "ERR:", result
                        
## Validate, compile and evaluate code

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
    
             

# Contact
Write me: yaroslaff@gmail.com