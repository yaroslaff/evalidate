from evalidate import ExecutionException, ValidationException, Expr, base_eval_model
import pytest 

class TestJailbreak():
    def test_ossystem_nocall(self):
        # must fail because calls are not allowed at all
        with pytest.raises(ValidationException):
            Expr('os.system("clear")')

    def test_ossystem_call_int(self):
        # must fail because this function not allowed
        with pytest.raises(ValidationException):
            m = base_eval_model.clone()
            m.nodes.append('Call')
            m.allowed_functions.append('int')

            Expr('os.system("clear")', model=m)

    def test_ossystem_import(self):
        # must fail anyway
        with pytest.raises(ValidationException):
            m = base_eval_model.clone()
            m.nodes.append('Call')
            m.allowed_functions.append('int')
            Expr("__import__('os').system('clear')", model=m)

    def test_builtins(self):
        # indirect call
        src="""__builtins__['eval']("print(1)")""" 
        with pytest.raises(ValidationException):
            m = base_eval_model.clone()
            m.nodes.append('Call')
            result = Expr(src, model=m)
         
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

        m = base_eval_model.clone()
        m.nodes.append('Call')

        for bomb in bomb_list:
            with pytest.raises(ValidationException):
                Expr(expr=bomb, model=m)

    def test_mul_overflow(self):
        src = '"a"*1000000*1000000*1000000*1000000'
        with pytest.raises(ExecutionException):
            m = base_eval_model.clone()
            m.nodes.append('Mult')
            Expr(src, model=m).eval()
