import argparse
import sys

from kaa.repl import Repl
from kaa.runtime import Runtime


def main():
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
    elif sys.stdin.isatty():
        Repl(runtime).loop()

    else:
        runtime.eval_file(sys.stdin)


if __name__ == '__main__':
    main()
