# from evalidate import ExecutionException, ValidationException, Expr, base_eval_model
from evalidate import Expr, base_eval_model, ValidationException, ExecutionException
from copy import deepcopy
from collections import UserDict


class TestNoMutation():

    def test_no_mutation_globals(self):
        expr = Expr('a + b')
        ctx = dict(a=1, b=2)
        ctx_orig = deepcopy(ctx)
        result = expr.eval(ctx_globals=ctx)
        assert result == 3
        assert ctx == ctx_orig


    def test_no_mutation_locals(self):
        expr = Expr('a + b')
        ctx = dict(a=1, b=2)
        ctx_orig = deepcopy(ctx)
        result = expr.eval(ctx_locals=ctx)
        assert result == 3
        assert ctx == ctx_orig

