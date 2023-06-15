from evalidate import Expr, EvalException, ValidationException
import pytest

class TestExpr():
    def test_basic(self):
        r = Expr('1+2').eval()
        assert r == 3

    def test_mult(self):
        with pytest.raises(ValidationException):
            r = Expr('42 * 42').eval()
        
        r = Expr('42 * 42', nodes=['Mult']).eval()
        assert r == 1764 

    def test_blank(self):
        with pytest.raises(ValidationException):
            r = Expr('1 + 2', blank=True).eval()

        r = Expr('1 + 2', blank=True, nodes=['Expression', 'BinOp', 'Constant', 'Add']).eval()
        assert r == 3

    def test_cleanup(self):
        ctx=dict()
        Expr('None').eval(ctx)
        assert '__builtins__' not in ctx

    def test_context(self):
        e = Expr('a + b')
        assert e.eval({'a': 1, 'b': 2}) == 3
        assert e.eval({'a': 0, 'b': 2}) == 2        
    
    def test_functions(self):
        with pytest.raises(ValidationException):
            r = Expr('int(x)').eval({'x': 1.3})

        r = Expr('int(x)', nodes=['Call'], funcs=['int']).eval({ "x": 1.3 })
        assert r == 1
    
    def test_attributes(self):
        
        class Person:
            pass

        class Movie:
            pass

        person = Person()

        person.name = 'Audrey Hepburn'
        person.birth = 1929


        movie1 = Movie()
        movie1.title = "Roman Holiday"
        movie1.year = 1953

        movie2 = Movie()
        movie2.title = "Breakfast at Tiffany's"
        movie2.year = 1961

        movies = [movie1, movie2]


        with pytest.raises(ValidationException):
            r = Expr('movie.year - person.birth').eval({"person": person, "movie": movie1})
        
        e = Expr('movie.year - person.birth', nodes=['Attribute'], attrs=['year', 'birth'])

        age = e.eval({"person":person, "movie": movie1})
        assert age == 24

        age = e.eval({"person": person, "movie": movie2})
        assert age == 32

        ages = [ e.eval({"person": person, "movie": movie}) for movie in movies ]
        assert ages == [ 24, 32 ]


    def test_dicts(self):
        person = {
            'name': 'Audrey Hepburn',
            'birth': 1929
        }
        movies = [
            {
                'title': "Roman Holiday",
                'year': 1953
            },
            {
                'title': "Breakfast at Tiffany's",
                'year': 1961
            }
        ]

        e = Expr('movie["year"] - person["birth"]')

        ages = [ e.eval({"movie": movie, "person": person}) for movie in movies ]
        assert ages == [24,32]
    
    def test_my_funcs(self):
        def double(x):
            return x * 2

        ctx = {'a': 123.456}
        e = Expr('int(a) + double(a)', nodes=['Call'], funcs=['double', 'int'], my_funcs={'double': double})
        r = e.eval(ctx)
        print(r)
        print(ctx)