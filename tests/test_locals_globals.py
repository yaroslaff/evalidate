# from evalidate import ExecutionException, ValidationException, Expr, base_eval_model
from evalidate import Expr, base_eval_model, ValidationException, ExecutionException
import pytest 
from collections import UserDict


class LazyDict(UserDict):
    def __missing__(self, key):
        return 42


class TestLocalsGlobals():

    def test_locals(self):
        expr = Expr('a + b')
        ctx = dict(a=1, b=2)
        result = expr.eval(None, ctx)
        assert result == 3

    def test_globals(self):
        expr = Expr('a + b')
        ctx = dict(a=1, b=2)
        result = expr.eval(ctx)
        assert result == 3

    def test_list_comprehension(self):

        # prepare model
        my_model = base_eval_model.clone()
        my_model.nodes.extend(
            [
                "Call",
                "Attributes",
                "ListComp",
                "DictComp",
                "comprehension",
                "Store",
                "ForOfStatement",
                "Subscript",
                "GeneratorExp",
                "For",
            ]
        )
        my_model.allowed_functions.append("sum")

        my_shelve = {
            "height": 200,
            "boxes": {
                "box1": {"volume": 110},
                "box2": {"volume": 90},
            },
            "column_width": [20, 480, 40],
        }

        exp_string = "sum([my_shelve['boxes'][box]['volume'] for box in my_shelve['boxes'] ])"
        exp = Expr(exp_string, my_model)
        res = exp.eval({"my_shelve": my_shelve})
        assert res == 200

    def test_userdict(self):
        ctx = LazyDict(a=100)
        expr = Expr("a+b")
        
        # must raise exception
        with pytest.raises(ExecutionException):
            res = expr.eval(ctx_globals=ctx)

        res = expr.eval(ctx_locals=ctx)
        assert res == 142

