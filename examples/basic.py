#!/usr/bin/env python3

from evalidate import Expr, EvalException

src = 'a + 40 > b'
# src="__import__('os').system('clear')"

try:
    print(Expr(src).eval({'a':10, 'b':42}))
except EvalException as e:
    print(e)
