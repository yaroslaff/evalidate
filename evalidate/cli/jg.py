#!/usr/bin/env python3

from evalidate import Expr, ValidationException, CompilationException, ExecutionException
import json
import sys
import argparse
import time

def short_repr(data, limit=100):
    try:
        text = json.dumps(data, ensure_ascii=False)
    except Exception:
        text = repr(data)
    if len(text) > limit:
        text = text[:limit] + "..."
    return text

def get_args():
    parser = argparse.ArgumentParser('Grep JSON files by python expression')
    parser.add_argument('-b', '--benchmark', default=False, action='store_true', help='Do not print, just search and measure search time')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Be verbose')
    parser.add_argument('-l', '--jsonl', default=False, action='store_true', help='input is JSONL (not JSON list)')
    parser.add_argument('-k', '--keypath', type=str, help='key path to list separated by ::, e.g.: -k shop::products::onstock')
    parser.add_argument('-f', '--format', type=str, help='format (if not JSON), e.g. -f \'{sku} {price} ({stock}) {title!r}\'')
    parser.add_argument('expr', help='Python filter expression')
    parser.add_argument('path', default=None, help='Path to JSON list (or stdin)', nargs='?')

    return parser.parse_args()

    

def vprint(s: str):
    if args.verbose:
        print(s)

def main():
    global args

    args = get_args()
    if args.benchmark:
        args.verbose = True
    out = list()

    vprint(f'# loading data from {args.path or "stdin"}')

    if args.path:
        f = open(args.path, "r", encoding="utf-8")
    else:
        f = sys.stdin

    with f:
        if args.jsonl:
            data = [json.loads(line) for line in f if line.strip()]
        else:
            data = json.load(f)

    # follow keypath if needed
    try:
        if args.keypath:
            for k in args.keypath.split('::'):
                data = data[k]
    except KeyError as e:
        print(f"No such key: {e}", file=sys.stderr)
        sys.exit(1)

    vprint(f'# loaded {len(data)} records from {args.path}')

    try:    
        expr = Expr(args.expr)
    except (ValidationException, CompilationException) as e:
        print(e)
        sys.exit(1)

    c=0
    start = time.time()

    if not isinstance(data, list):
        print("data is not a list", file=sys.stderr)
        print(short_repr(data))
        sys.exit(1)

    for p in data:
        try:
            # we use native eval with validated code to get better speed
            r = eval(expr.code, dict(), p)
            if r:
                out.append(p)
                c+=1
        except KeyError as e:
            pass
            # print("Runtime exception:", e)

    elapsed = round(time.time() - start, 2)

    vprint(f"# {c}/{len(data)} elements found in {elapsed} seconds".format(c))    
    if not args.benchmark:
        if args.format:
            for el in out:
                print(args.format.format(**el))
        else:    
            print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()