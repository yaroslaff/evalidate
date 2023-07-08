#!/usr/bin/python

"""Safe user-supplied python expression evaluation."""

import ast
import dataclasses
from typing import Callable

__version__ = '2.0.2'


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


@dataclasses.dataclass
class EvalModel:
    """ eval security model """
    nodes: list
    allowed_functions: list = dataclasses.field(default_factory=list)
    imported_functions: dict = dataclasses.field(default_factory=dict)
    attributes: list = dataclasses.field(default_factory=list)

    def clone(self):
        return EvalModel(**dataclasses.asdict(self))


class SafeAST(ast.NodeVisitor):

    """AST-tree walker class."""

    def __init__(self, model: EvalModel):
        self.model = model

    def generic_visit(self, node):
        """Check node, raise exception if node is not in whitelist."""

        if type(node).__name__ in self.model.nodes:

            if isinstance(node, ast.Attribute):
                if node.attr not in self.model.attributes:
                    raise ValidationException(
                        "Attribute {aname} is not allowed".format(
                            aname=node.attr))

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in self.model.allowed_functions and node.func.id not in self.model.imported_functions:
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


base_eval_model = EvalModel(
    nodes = [
                # 123, 'asdf'
                'Num', 'Str',
                # any expression or constant
                'Expression', 'Constant',
                # == ...
                'Compare', 'Eq', 'NotEq', 'Gt', 'GtE', 'Lt', 'LtE',
                # variable name
                'Name', 'Load',
                'BinOp',
                'Add', 'Sub', 'USub',
                'Subscript', 'Index',  # person['name']
                'BoolOp', 'And', 'Or', 'UnaryOp', 'Not',  # True and True
                "In", "NotIn",  # "aaa" in i['list']
                "IfExp",  # for if expressions, like: expr1 if expr2 else expr3
                "NameConstant",  # for True and False constants
                "Div", "Mod"
            ],
)

mult_eval_model = base_eval_model.clone()
mult_eval_model.nodes.append('Mul')

class Expr():
    def __init__(self, expr, model=None, filename=None):
        self.expr = expr
        self.model = model or base_eval_model

        try:
            self.node = ast.parse(self.expr, '<usercode>', 'eval')
        except SyntaxError as e:
            raise CompilationException(e)

        v = SafeAST(model = self.model)
        v.visit(self.node)

        self.code = compile(self.node, filename or '<usercode>', 'eval')

    def eval(self, ctx=None):
        
        try:
            result = eval(self.code, self.model.imported_functions, ctx)
        except Exception as e:
            raise ExecutionException(e)

        return result
    
    def __str__(self):
        return("Expr(expr={expr!r})".format(expr=self.expr))
