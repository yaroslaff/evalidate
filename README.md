# About Evalidate
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) logical expressions in python syntax.

# Purpose
Originally it's developed for filtering (performing boolean expressions) complex data structures e.g. raise salary if 

    person.age>30 and person.salary>5000 or "Jack" in person.children

or, like simple firewall, allow inbound traffic if:

    packet.tcp.dstport==22 and packet.tcp.srcip in myip

But also, it can be used for other expressions, e.g. arithmetical, like
    a+b-100
    
# Security
Built-in python features such as compile, eval is quite powerful to run any kind of user-supplied code, but could be insecure if used code is malicious like os.system("rm -rf /"). Evalidate works on whitelist principle, allowing code only if it consist only  of safe operations (based on authors views about what is safe and what is not, your mileage may vary - but you can supply your list of safe operations)

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
    ERROR: Compilation error: Operaton type Call is not allowed
    
# Extending evalidate, safenodes and addnodes
Evalidate has built-in set of python operations, which are considered 'safe' (from author point of view). Code is considered valid only if all of it's operations are in this list. You can override this list by adding argument *safenodes* like:
    
    success,result = evalidate.safeeval(src,c, safenodes=['Expression','BinOp','Num','Add'])

this will be enough for '1+1' expression (in src argument), but not for '1-1'. If you will try '1-1', it will report error:

    ERROR: Compilation error: Operaton type Sub is not allowed.

This way you can start from scratch and allow only required operations. As an alternative, you can use built-in list of allowed operations and extend it if needed, using *addnodes* argument.

For example, "1*1" will give error:

  ERROR: Compilation error: Operaton type Mult is not allowed

But it will work with addnodes:

    success,result = evalidate.safeeval(src,c, addnodes=['Mult'])
    
Please note, using 'Mult' operation isn't very secure, because for strings it can lead to Out-of-memory:

    src='"a"=="a"*100*100*100*100*100'
    
    ERROR: Runtime error (OverflowError): repeated string is too long

    
# Functions

## success,result = safeeval(src,context={}, safenodes=None, addnodes=None)
safeeval - is higher-level function of module, which validates code and runs it (if validation is successful)

src - source expression like "person['Age']>30 and salary==10000"

context - dictionary of variables, available for evaluated code.

return values:

success - binary, True if validation is successul and evaluation didn't thrown any exceptions. (False in this case) 

result - if success==True, result is result of expression. If success==False, result is string with error message, like "ERROR: Runtime error (NameError): name 'aaa' is not defined"
    
safeeval doesn't throws any exceptions    
    
## node = evalidate(expression,safenodes=None,addnodes=None)
evalidate() performs parsing of python expession, validates it, and returns python AST (Abstract Syntax Tree) structure, which can be later compiled and executed

    code = compile(node,'<usercode>','eval')
    eval(code)
    
Even if evalidate is successful, this doesn't guarantees that code will run well, For example, if can have NameError (if tries to access undefined variable) or ZeroDivisionError.

