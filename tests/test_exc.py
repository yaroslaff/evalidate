from evalidate import Expr, ValidationException, ExecutionException, CompilationException, base_eval_model
import pytest

class TestExceptions():
    def test_exec(self):
        with pytest.raises(ExecutionException) as e:
            r = Expr('1/0').eval()

        with pytest.raises(ExecutionException) as e:
            r = Expr('1+x').eval()

    def test_badcode(self):

        with pytest.raises(CompilationException) as e: 
            r = Expr('')

        with pytest.raises(CompilationException) as e: 
            r = Expr(';')

        with pytest.raises(CompilationException) as e: 
            r = Expr("""
            1+1
            2+2""")

    def test_call(self):
        ctx = {'a':36.6}
        with pytest.raises(ValidationException) as e:
            r = Expr('int(a)').eval(ctx)

    def test_return(self):
        with pytest.raises(CompilationException) as e: 
            Expr('return 42').eval()
    
    def test_startswith(self):
        with pytest.raises(ValidationException) as e:
            src = '"abcdef".startswith("abc")'
            m = base_eval_model.clone()
            m.nodes.append('Call')
            r = Expr(src).eval()

