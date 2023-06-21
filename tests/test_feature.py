import evalidate
import pytest

class TestSafeEval():
    def test_sum(self):
        r = evalidate.Expr('1+2').eval()
        assert(r==3)

    def test_context(self):
        ctx = {'a':100, 'b': 200 }
        r = evalidate.Expr('a+b').eval(ctx)
        assert(r==300)

    def test_call(self):
        ctx = {'a':36.6}

        m = evalidate.base_eval_model.clone()
        m.nodes.append('Call')
        m.allowed_functions.append('int')

        r = evalidate.Expr('int(a)', model=m).eval(ctx)
        assert(r==36)

    def test_normal(self):
        codelist = [
            ('1+1',2),
            ('a+b',3),
            ('int(pi)', 3)
        ]

        ctx={'a':1, 'b':2, 'pi': 3.14}

        m = evalidate.base_eval_model.clone()
        m.nodes.append('Call')
        m.allowed_functions.append('int')

        for src, r in codelist:
            result = evalidate.Expr(src, model=m).eval(ctx)
            assert(result==r)
    
    def test_stack(self):
        src='int(1)'
        m = evalidate.base_eval_model.clone()
        m.nodes.append('Call')
        m.allowed_functions.append('int')

        for i in range(199):
            src = f'int( {src} )'

        r = evalidate.Expr(src, model=m).eval()
        assert( r==1 )
    
    def test_startswith(self):

        m = evalidate.base_eval_model.clone()
        m.nodes.extend(['Call', 'Attribute'])
        m.allowed_functions.append('int')
        m.attributes.append('startswith')


        src = '"abcdef".startswith("abc")'
        r = evalidate.Expr(src, model=m).eval()
        assert r
