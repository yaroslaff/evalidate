#!/usr/bin/python

import ast
import sys

class SafeAST(ast.NodeVisitor):

    allowed = {}
    
    def __init__(self,safenodes=None,addnodes=None):

        if safenodes:
            self.allowed=safenodes
        else:
            values=['Num','Str'] # 123, 'asdf'
            expression=['Expression'] # any expression
            compare=['Compare','Eq','NotEq','Gt','GtE','Lt','LtE'] # ==
            variables=['Name','Load'] # variable name
            binop=['BinOp']
            arithmetics=['Add','Sub']
            subscript=['Subscript','Index'] # person['name']
            boolop=['BoolOp','And','Or','UnaryOp','Not'] # True and True
            inop=["In"] # "aaa" in i['list']
            self.allowed = expression+values+compare+variables+binop+arithmetics+subscript+boolop+inop


        if addnodes:
            self.allowed = self.allowed + addnodes

    def generic_visit(self, node):

        if type(node).__name__ in self.allowed:
            #print "GOOD GENERIC ", type(node).__name__
            ast.NodeVisitor.generic_visit(self, node)
        else:
            raise ValueError("Operaton type {optype} is not allowed".format(optype=type(node).__name__))


def evalidate(expression,safenodes=None,addnodes=None):
    node = ast.parse(expression,'<usercode>','eval')

    v = SafeAST(safenodes,addnodes)
    v.visit(node)
    return node

def safeeval(src,context={}, safenodes=None, addnodes=None):
    try:
        node=evalidate(src, safenodes, addnodes)
    except ValueError as ve:
        print "ValueError:",ve
        return (False,"Compilation error: "+ve.__str__())
    except SyntaxError as se:
        return (False,"Compilation error: "+se.__str__())
    code = compile(node,'<usercode>','eval')

    try:
        result = eval(code,context)
    except Exception as e:
        et,ev,erb = sys.exc_info()
        return False,"Runtime error ({}): {}".format(type(e).__name__,ev)
       

    return (True,result)


if __name__=='__main__':
    src='i[bbb]'

    i={}
    i['name']="hello"
    i['age']=33
    i['child']=["aaa","bbb","ccc"]
    i['a']={}
    i['a']['one']='one'
    i['a']['two']=2

    env={'a':22,'b':33,'c': 55,'i':i,'hello':'hello','time':100,'now':200}   
    

    print "src: ",src
    print "env: ",env
    success,result = safeeval(src,env)
    
    if success:
        print "result: ",result 
    else:
        print "ERR: ",result
