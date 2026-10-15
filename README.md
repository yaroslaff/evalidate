# Evalidate

Evalidate is a simple Python library for safely evaluating untrusted, user-supplied Python expressions. It validates expressions before execution and rejects potentially malicious code.

Evalidate also comes with a convenient, high-performance CLI tool, `jg`, for filtering JSON lists using Python expressions:

```shell
jg 'attributes["storage"] == "512GB" and price<300 and rating>4' products.json
```

## Purpose

Evalidate was originally developed to filter complex data structures. For example, to find inexpensive smartphones that are available for sale:

```python
category=="smartphones" and price<300 and stock>0
```

However, it can also evaluate other types of expressions, including arithmetic expressions:

```python
a+b-100
```

Evalidate is the fastest secure Python `eval()` alternative I know of.

## Installation

```shell
pip3 install evalidate
```

## TL;DR: Just give me safe `eval()`!

```python
from evalidate import base_eval_model, EvalException

src = 'a + 10 > b'
# src = "__import__('os').system('clear')"

model = base_eval_model.clone()
expr = model.expr(src)

try:
    print(expr.eval({'a':10, 'b':142}))
except EvalException as e:
    print(e)
```

Output:

```
True
```

If you try to execute the potentially dangerous expression (uncomment the second `src` line), the output will be:

```
ERR: Operation type Call is not allowed
```

Here's a more practical example: finding inexpensive smartphones that meet specific requirements.

```python
from evalidate import base_eval_model, EvalException

mobiles = [
    {'brand': 'Apple',    'model': 'iPhone 15',              'price': 799,  'RAM': 6,  'storage': 128},
    {'brand': 'Apple',    'model': 'iPhone 14',              'price': 799,  'RAM': 6,  'storage': 128},
    {'brand': 'Samsung',  'model': 'Galaxy S23 Ultra',       'price': 1199, 'RAM': 8,  'storage': 256},
    {'brand': 'Samsung',  'model': 'Galaxy A54',             'price': 449,  'RAM': 8,  'storage': 128},
    {'brand': 'Samsung',  'model': 'Galaxy Z Flip 5',        'price': 999,  'RAM': 8,  'storage': 256},
    {'brand': 'Google',   'model': 'Pixel 8',                'price': 699,  'RAM': 8,  'storage': 128},
    {'brand': 'Google',   'model': 'Pixel 7a',               'price': 499,  'RAM': 8,  'storage': 128},
    {'brand': 'OnePlus',  'model': 'OnePlus 11',             'price': 699,  'RAM': 16, 'storage': 256},
    # intentionally incomplete:
    {'brand': 'Xiaomi',   'model': 'Xiaomi 13 Pro',          'price': 999,  'RAM': 12, },
    {'brand': 'Xiaomi',   'model': 'Redmi Note 12 Pro',      'price': 299,  'RAM': 8,  'storage': 256},
]

src = 'storage >= 256 and RAM >= 8 and price <= 1000'

model = base_eval_model.clone()
try:
    expr = model.expr(src)
except EvalException as e:
    print(f"Error in expression ({src}): {e}")
    exit(1)

for mobile in mobiles:
    try:
        if expr.eval(mobile):
            print(f"{mobile['brand']} {mobile['model']} {mobile['storage']}/{mobile['RAM']} ({mobile['price']})")

    except EvalException as e:
        print(f"ERROR: evaluating expression for {mobile['brand']} {mobile['model']}: {e}")
```

## Security

Python's built-in functions, such as `compile()` and `eval()`, are powerful enough to execute arbitrary user-supplied code. Using them with untrusted input can therefore be dangerous. For example, an expression might attempt to execute `os.system("rm -rf /")`.

Evalidate uses a whitelist-based approach: an expression is accepted only if it consists of operations explicitly permitted by the configured security model. What counts as safe depends on the model's configuration and the author's security assumptions. Your requirements may differ, so you can define your own list of allowed operations.

Although the built-in models are designed to be secure, Evalidate allows you to extend them. Do so carefully: even an attribute that appears harmless, such as `.format`, can introduce vulnerabilities.

## Exceptions

Evalidate defines three exception classes: `CompilationException`, `ValidationException`, and `ExecutionException`. All three inherit from the base exception class `EvalException`.

## Models: Configuring Validation

Evalidate is highly configurable. Whether an expression passes validation or raises an exception depends on the security model used.

`EvalModel` defines the security policy for expression evaluation. It specifies the allowed AST nodes, function calls, and attributes, as well as a dictionary of imported functions. Evalidate provides a built-in model, `base_eval_model`, which permits a basic set of operations considered safe by the author.

You can create an empty model and extend it as needed:

```python
my_model = evalidate.EvalModel()
```

By default, an empty model allows no operations. Even `1+2` is rejected.

Alternatively, you can clone `base_eval_model` and extend it:

```python
from evalidate import Expr, base_eval_model

my_model = base_eval_model.clone()
my_model.nodes.append('Mult')

expr = my_model.expr('2*2')
expr.eval()
```

To enable calls to `int()`, allow the `Call` node and add `int` to the list of permitted functions:

```python
my_model.nodes.append('Call')
my_model.allowed_functions.append('int')

my_model.expr('int(36.6)').eval()
```

To enable attribute access and method calls, configure the model as follows:

```python
m = base_eval_model.clone()
m.nodes.extend(['Call', 'Attribute'])
m.attributes.append('startswith')

src = '"abcdef".startswith("abc")'

r = m.expr(src).eval()
print(r)
```

Even with this configuration, an expression such as `__builtins__["eval"](1)` is rejected.

### Exporting Functions to Expressions

You can explicitly expose your own functions to evaluated expressions:

```python
from evalidate import base_eval_model

def one():
    return 1

m = base_eval_model.clone()
m.nodes.append('Call')
m.imported_functions["one"] = one
m.expr('one()').eval()
```

### Testing a Model's Security

Evalidate includes a built-in collection of potential attacks and a `test_security()` method that tests a model against them.

Passing `test_security()` is necessary, but not sufficient, to establish that a model is secure. Even if `test_security()` returns `True`, the model may still be vulnerable to attacks that the test suite does not cover.

```python
from evalidate import base_eval_model

m = base_eval_model.clone()
m.nodes.append('Pow')

assert(m.test_security())

src = '10**10**10'
m.expr(src).eval()
```

## CLI Tools

### `genfakeproducts`

`genfakeproducts` generates a JSON array containing a specified number of fake product records for testing.

For example, to generate one million records (this takes about one minute on my computer):

```shell
genfakeproducts -n 1000000 -o products.json
```

By default, it generates 10,000 records and writes them to `products.json`. This takes approximately one second.

Example record:

```json
{
  "id": "d5af9f93-c164-4872-a535-4fb56cf62e6e",
  "sku": "SKU-D5AF9F93",
  "title": "Google ET-3843 Pro",
  "brand": "Google",
  "category": "phones",
  "description": "Foot trial city avoid he wish real college investment tend include draw window either over somebody history detail risk support glass. Google phones designed for modern users.",
  "price": 340.94,
  "currency": "USD",
  "stock": 24,
  "rating": 4.23,
  "reviews_count": 222,
  "attributes": {
    "storage": "512GB",
    "color": "red"
  },
  "tags": [
    "limited",
    "new"
  ]
}
```

To use `genfakeproducts`, install Evalidate with the `generate` extra:

```shell
pip3 install evalidate[generate]
```

### `jg` (JSON grep)

`jg` is a high-performance CLI tool for filtering JSON data using Python expressions. It accepts an expression and a filename, or reads input from standard input.

```
jg 'category=="phones"' products.json
```

`jg` implements only a small subset of `jq`'s functionality, but it is twice as fast and much simpler to use.

**Options**

- `-b` — Benchmark mode. Suppresses JSON output and measures filtering time.
- `-v` — Verbose mode.
- `-l` — Read input as JSON Lines (JSONL), with one JSON object per line, instead of a JSON array.
- `-k` — Specify the key path to the list, such as `"shop::products::onstock"`, when the input is a nested dictionary.
- `-f` — Specify a custom output format for non-JSON output, e.g. `'{sku} {price} ({stock}) {title!r}'`.

## Advanced Topics

### Improve Performance by Using Native `eval()` on Validated Code

Evalidate is fast, but its evaluation machinery still introduces some overhead. If you need maximum performance, you can use Python's native [`eval()`](https://docs.python.org/3/library/functions.html#eval) directly on the validated code:

```python
from evalidate import base_eval_model

m = base_eval_model.clone()
d = dict(a=1, b=2)
expr = m.expr('a+b')
r = eval(expr.code, None, d) # <-- native python eval, will run at eval() speed
print(r)
```

This approach provides the same expression-validation guarantees as `Model.Expr.eval()`, because `expr.code` has already passed validation.

The differences are minor but important: executing `expr.code` directly can raise arbitrary exceptions, whereas `expr.eval()` raises only `ExecutionException`. Also, if you want to expose functions to the expression, you must do so manually.

### Custom Mapping Classes

You can use custom mapping classes instead of `dict`. As with native Python `eval()`, a custom mapping class can be used only as the local evaluation context.

Example:

```python
from collections import UserDict
from evalidate import base_eval_model

class LazyDict(UserDict):
    def __missing__(self, key):
        return 42

ctx = LazyDict(a=100)

model = base_eval_model.clone()

expr = model.expr("a+b")

res = expr.eval(ctx_locals=ctx)
print(res) # 142
```

### Limitations

Evalidate uses [`ast.parse()`](https://docs.python.org/3/library/ast.html#ast.parse) to generate an [abstract syntax tree (AST)](https://docs.python.org/3/library/ast.html#node-classes), which it then validates.

> **Warning**
>
> A sufficiently large or deeply nested input string can crash the Python interpreter because of stack-depth limitations in Python's AST compiler.

In my tests, expressions containing 200 nested `int()` calls work:

```
int(int(.... int(1)...))
```

but expressions with 201 nested calls do not. The source code is over 1,000 characters long. Even if Evalidate receives such an expression, it will raise `CompilationException`.

## Similar Projects and Benchmarks

### [asteval](https://newville.github.io/asteval/)

`asteval` supports more complex code, including function definitions and access to Python's mathematical libraries. However, it has two drawbacks:

- It is significantly slower than Evalidate, which can evaluate validated code at native `eval()` speed.
- User-supplied expressions can run for a long time and consume excessive resources.

### [simpleeval](https://github.com/danthedeckie/simpleeval)

`simpleeval` is a similar project that also uses an AST-based approach and is optimized for repeatedly evaluating pre-parsed expressions.

However, it evaluates expressions using a higher-level representation based on [`ast.Expr`](https://docs.python.org/3/library/ast.html#ast.Expr), which makes evaluation several times slower. Evalidate instead compiles validated expressions into Python's native `code` objects, allowing execution at native `eval()` speed.

Evalidate is particularly well suited to evaluating the same expression against many different data objects.

## Benchmarking

The benchmark script is `benchmark/benchmark.py` in this repository.

The benchmark creates a list of one million products. In practice, it takes a sample of 100 products and repeats it 10,000 times. It then filters the list using an untrusted user-supplied expression to find matching products. The expression in this test is `price < 20`.

```
Products: 1000000 items
evalidate_raw_eval(): 0.266s
evalidate_eval(): 0.326s
test_simpleeval(): 1.824s
test_asteval(): 26.106s
```

As the results show, Evalidate is several times faster than `simpleeval`, and both are significantly faster than `asteval`.

The benchmark may not be optimally implemented; I am not an expert in `simpleeval` or `asteval`. If you can suggest a faster filtering implementation, I will consider including it. Any proposed benchmark code must treat the expression as unknown in advance and potentially untrusted.

## Further Reading: The Risks of `eval()`

- [Eval really is dangerous](https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html)
- [Breaking Python 3 eval protections](https://netsec.expert/posts/breaking-python3-eval-protections/)
- [Python eval() function](https://realpython.com/python-eval-function/)

**Note:** The Real Python article demonstrates a concise source-validation technique based on `code.co_names`. However, this technique is vulnerable: it accepts the "bomb" from Ned Batchelder's article, which has an empty `co_names` tuple and can crash the interpreter.

Evalidate can reject this code and similar bombs, unless you deliberately configure the model to allow the specific operations required by an attack. Evalidate makes it harder to shoot yourself in the foot, but it is still possible if you try hard enough.

## More Information

For more information, see the module's source code. It is short, straightforward, and easy to modify.

## Contact

Email: yaroslaff at gmail.com
