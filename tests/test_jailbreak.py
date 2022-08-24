from evalidate import ExecutionException, safeeval, ValidationException
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
            result = safeeval(src, addnodes=["Call"])
         
    def test_bomb(self):
        bomb_list = ["""
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            0,0,0,0,0,b"BOOM",(),(),(),"","",0,b""
        ),{}
    )()
)()
""",
"""
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            0,0,0,0,0,0,b"BOOM",(),(),(),"","",0,b""
        ),{}
    )()
)()
""",
"""
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            0,0,0,0,0,0,b"BOOM",(),(),(),"","","",0,b"",b"",b"",b"",(),()
        ),{}
    )()
)()
"""
]
        for bomb in bomb_list:
            with pytest.raises(ValidationException):
                safeeval(bomb, addnodes=["Call"])

    def test_mul_overflow(self):
        src = '"a"*1000000*1000000*1000000*1000000'
        with pytest.raises(ExecutionException):
            safeeval(src, addnodes=['Mult'])
