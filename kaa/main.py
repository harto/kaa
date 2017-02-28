from kaa.runtime import Runtime
import argparse
import sys

def boot():

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
            runtime.eval_file(path)

    elif sys.stdin.isatty():
        from .repl import Repl
        Repl(runtime).loop()

    else:
        runtime.eval_lines(sys.stdin)

if __name__ == '__main__':
    boot()
