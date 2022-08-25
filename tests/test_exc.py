from evalidate import ValidationException, evalidate, safeeval, ExecutionException, CompilationException
import pytest

class TestExceptions():
    def test_exec(self):
        with pytest.raises(ExecutionException) as e:
            r = safeeval('1/0')

        with pytest.raises(ExecutionException) as e:
            r = safeeval('1+x')

    def test_badcode(self):

        with pytest.raises(CompilationException) as e: 
            r = safeeval('')

        with pytest.raises(CompilationException) as e: 
            r = safeeval(';')

        with pytest.raises(CompilationException) as e: 
            r = safeeval("""
            1+1
            2+2""")

    def test_call(self):
        ctx = {'a':36.6}
        with pytest.raises(ValidationException) as e:
            r = safeeval('int(a)', ctx)

    def test_return(self):
        with pytest.raises(CompilationException) as e: 
            evalidate('return 42')
    
