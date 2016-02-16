import argparse
from runtime import Runtime
import sys

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('paths',
                        metavar='file',
                        nargs='*',
                        help='lisp file(s) to evaluate')

    parser.add_argument('--expression',
                        help='lisp expression to evaluate')

    args = parser.parse_args()

    runtime = Runtime()

    if args.expression:
        runtime.eval_string(args.expression)

    elif args.paths:
        for path in args.paths:
            with open(path) as f:
                runtime.eval_file(f)

    else:
        print('todo: read forms from stdin or boot repl')
