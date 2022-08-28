#!/usr/bin/python

"""Safe user-supplied python expression evaluation."""

import ast
import sys


class EvalException(Exception):
    pass

class ValidationException(EvalException):
    pass

class CompilationException(EvalException):
    exc = None
    def __init__(self, exc):
        super().__init__(exc)
        self.exc = exc

class ExecutionException(EvalException):
    exc = None
    def __init__(self, exc):
        super().__init__(exc)
        self.exc = exc


class SafeAST(ast.NodeVisitor):

    """AST-tree walker class."""

    allowed = {}

    def __init__(self, safenodes=None, addnodes=None, funcs=None, attrs=None):
        """create whitelist of allowed operations."""
        if safenodes is not None:
            self.allowed = safenodes
        else:
            # 123, 'asdf'
            values = ['Num', 'Str']
            # any expression or constant
            expression = ['Expression']
            constant = ['Constant']
            # == ...
            compare = ['Compare', 'Eq', 'NotEq', 'Gt', 'GtE', 'Lt', 'LtE']
            # variable name
            variables = ['Name', 'Load']
            binop = ['BinOp']
            arithmetics = ['Add', 'Sub']
            subscript = ['Subscript', 'Index']  # person['name']
            boolop = ['BoolOp', 'And', 'Or', 'UnaryOp', 'Not']  # True and True
            inop = ["In", "NotIn"]  # "aaa" in i['list']
            ifop = ["IfExp"] # for if expressions, like: expr1 if expr2 else expr3
            nameconst = ["NameConstant"] # for True and False constants
            div = ["Div", "Mod"]

            self.allowed = expression + constant + values + compare + \
                variables + binop + arithmetics + subscript + boolop + \
                inop + ifop + nameconst + div

        self.allowed_funcs = funcs or list()
        self.allowed_attrs = attrs or list()

        if addnodes is not None:
            self.allowed = self.allowed + addnodes

    def generic_visit(self, node):
        """Check node, raise exception if node is not in whitelist."""
        
        if type(node).__name__ in self.allowed:

            if isinstance(node, ast.Attribute):
                if node.attr not in self.allowed_attrs:
                    raise ValidationException(
                        "Attribute {aname} is not allowed".format(
                            aname=node.attr))    
                        

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in self.allowed_funcs:
                        raise ValidationException(
                            "Call to function {fname}() is not allowed".format(
                                fname=node.func.id))    
                    else:
                        # Call to allowed function. good. No exception
                        pass            
                elif isinstance(node.func, ast.Attribute):
                    pass
                    # print("attr:", node.func.attr)                                        
                else:
                    raise ValidationException('Indirect function call')

            ast.NodeVisitor.generic_visit(self, node)
        else:
            raise ValidationException(
                "Operation type {optype} is not allowed".format(
                    optype=type(node).__name__))


def evalidate(expression, safenodes=None, addnodes=None, funcs=None, attrs=None):
    """Validate expression.

    return node if it passes our checks
    or pass exception from SafeAST visit.
    """
    try:
        node = ast.parse(expression, '<usercode>', 'eval')
    except SyntaxError as e:
        raise CompilationException(e)


    v = SafeAST(safenodes, addnodes, funcs, attrs)
    v.visit(node)
    return node


def safeeval(expression, context={}, safenodes=None, addnodes=None, funcs=None, attrs=None):
    """C-style simplified wrapper, eval() replacement."""

    # ValidationException thrown here
    node = evalidate(expression, safenodes, addnodes, funcs, attrs)

    code = compile(node, '<usercode>', 'eval')

    wcontext = context.copy()
    try:
        result = eval(code, wcontext)
    except Exception as e:
        raise ExecutionException(e)

    return result
