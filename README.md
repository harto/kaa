Kaa
===

A toy Lisp implementation in Python 3.

Named after the [Jungle Book character](https://en.wikipedia.org/wiki/Kaa). It
also sounds like the Australian pronunciation of
[`car`](https://en.wikipedia.org/wiki/CAR_and_CDR).


Development
-----------

```console
make        # initial setup
make check  # run linter, test suite
```


Usage
-----

```console
kaa                                 # boot a REPL
kaa some-file.lisp                  # eval a source file
kaa --expression='(print (+ 1 2))'  # eval a single expression
echo '(print (+ 1 2))' | kaa        # eval lines from stdin
```
