import evalidate
import pytest

class TestSafeEval():
    def test_sum(self):
        r = evalidate.safeeval('1+2')
        assert(r==3)

    def test_context(self):
        ctx = {'a':100, 'b': 200 }
        r = evalidate.safeeval('a+b', ctx)
        assert(r==300)

    def test_call(self):
        ctx = {'a':36.6}
        r = evalidate.safeeval('int(a)', ctx, addnodes=['Call'], funcs=['int'])
        assert(r==36)

    def test_normal(self):
        codelist = [
            ('1+1',2),
            ('a+b',3),
            ('int(pi)', 3)
        ]

        ctx={'a':1, 'b':2, 'pi': 3.14}

        for src, r in codelist:
            node = evalidate.evalidate(src, addnodes=['Call'], funcs=['int'])
            code = compile(node,'<usercode>','eval')
            result = eval(code, {}, ctx)
            assert(result==r)
    
    def test_stack(self):
        src='int(1)'
        for i in range(199):
            src = f'int( {src} )'
        r = evalidate.safeeval(src, addnodes=['Call'], funcs=['int'])
        assert( r==1 )
    
    def test_startswith(self):
        src = '"abcdef".startswith("abc")'
        r = evalidate.safeeval(src, addnodes=['Call', 'Attribute'], attrs=['startswith'])
