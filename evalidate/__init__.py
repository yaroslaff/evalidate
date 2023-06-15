#!/usr/bin/python

"""Safe user-supplied python expression evaluation."""

import ast

__version__ = '1.1.0'


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
            ifop = ["IfExp"]  # for if expressions, like: expr1 if expr2 else expr3
            nameconst = ["NameConstant"]  # for True and False constants
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
                "Node type {optype!r} is not allowed. (whitelist it manually)".format(
                    optype=type(node).__name__))


class Expr():
    def __init__(self, expr, nodes=None, blank=False, funcs=None, my_funcs=None, attrs=None, filename=None):
        self.expr = expr
        self.my_funcs = my_funcs

        # default nodes
        if blank:
            self.nodes = list()
        else:
            self.nodes = [
                # 123, 'asdf'
                'Num', 'Str',
                # any expression or constant
                'Expression', 'Constant',
                # == ...
                'Compare', 'Eq', 'NotEq', 'Gt', 'GtE', 'Lt', 'LtE',
                # variable name
                'Name', 'Load',
                'BinOp',
                'Add', 'Sub',
                'Subscript', 'Index',  # person['name']
                'BoolOp', 'And', 'Or', 'UnaryOp', 'Not',  # True and True
                "In", "NotIn",  # "aaa" in i['list']
                "IfExp",  # for if expressions, like: expr1 if expr2 else expr3
                "NameConstant",  # for True and False constants
                "Div", "Mod"
            ]

        self.funcs = funcs or list()
        if self.my_funcs:
            self.funcs.extend(self.my_funcs.keys())

        self.attrs = attrs or list()

        if nodes:
            self.nodes.extend(nodes)

        try:
            self.node = ast.parse(self.expr, '<usercode>', 'eval')
        except SyntaxError as e:
            raise CompilationException(e)

        v = SafeAST(safenodes=self.nodes, funcs=self.funcs, attrs=attrs)
        v.visit(self.node)

        self.code = compile(self.node, filename or '<usercode>', 'eval')

    def eval(self, ctx=None):
        
        try:
            result = eval(self.code, self.my_funcs, ctx)
        except Exception as e:
            raise ExecutionException(e)

        return result
    
    def __str__(self):
        return("Expr(expr={expr!r})".format(expr=self.expr))

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
    """C-style simplified wrapper, eval() replacement.

    Args:
        expr (str): the expression to evaluate

        safenodes (List[str] | None):
            Specify the name of allowed AST nodes, if unspecified a default list is used.

        addnodes (List[str] | None):
            List of additional AST node names to allow in addition to safenodes.

        funcs (List[str]):
            list of allowed function names.

        attrs (List[str]):
            list of allowed attribute names.

    Returns:
        Any: the result of the expression

    Raises:
        ExecutionException - if the expression fails to execute
        CompilationException - if the expression fails to parse
        ValidationException - if the expression fails safety checks

    Example:
        >>> import evalidate
        >>> evalidate.safeeval('3 + 2')
        5
        >>> evalidate.safeeval('max(3, 2)')
        Traceback (most recent call last):
            ...
        evalidate.ValidationException: Operation type Call is not allowed
        >>> evalidate.safeeval('max(3, 2)', addnodes=['Call'])
        Traceback (most recent call last):
            ...
        evalidate.ValidationException: Call to function max() is not allowed
        >>> evalidate.safeeval('max(3, 2)', addnodes=['Call'], funcs=['max'])
        3
    """

    # ValidationException thrown here
    node = evalidate(expression, safenodes, addnodes, funcs, attrs)

    code = compile(node, '<usercode>', 'eval')

    wcontext = context.copy()
    try:
        result = eval(code, wcontext)
    except Exception as e:
        raise ExecutionException(e)

    return result
