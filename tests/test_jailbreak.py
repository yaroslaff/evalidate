from evalidate import safeeval, ValidationException
import pytest 

class TestJailbreak():
    def test_ossystem_nocall(self):
        # must fail because calls are not allowed at all
        with pytest.raises(ValidationException):
            safeeval('os.system("clear")')

    def test_ossystem_call_int(self):
        # must fail because this function not allowed
        with pytest.raises(ValidationException):
            safeeval('os.system("clear")', addnodes=['Call'], funcs=['int'])

    def test_ossystem_import(self):
        # must fail anyway
        with pytest.raises(ValidationException):
            safeeval("__import__('os').system('clear')", addnodes=['Call'], funcs=['int'])

    def test_builtins(self):
        # indirect call
        src="""__builtins__['eval']("print(1)")""" 
        with pytest.raises(ValidationException):
            result = safeeval(src,addnodes=["Call"])
         
