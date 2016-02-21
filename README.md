Kaa
===

A toy Lisp implementation in Python.

Named after the [Jungle Book character](https://en.wikipedia.org/wiki/Kaa). It
also sounds like the Australian pronunciation of
[`car`](https://en.wikipedia.org/wiki/CAR_and_CDR).


Usage
-----

```
$ python -m kaa.main                                # boot a REPL
$ python -m kaa.main some-file.lisp                 # eval a source file
$ python -m kaa.main --expression='(print (+ 1 2))' # eval a single expression
$ echo '(print (+ 1 2)' | python -m kaa.main        # eval lines from stdin
```
