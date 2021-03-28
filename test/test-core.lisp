(print "test-core.lisp ")

(import (expect expect-raises) from kaa.test)

(expect-raises py/AssertionError (assert False))

(expect (list? ()))
(expect (list? (list)))
(expect (list? (list 1 2 3)))
(expect (not (list? "abc")))
(expect (not (list? 'def)))
(expect (not (list? True)))

(expect (empty? ()))
(expect (not (empty? '(1 2 3))))
(expect (not (empty? 'foo)))

(expect (symbol? 'some-symbol))
(expect (not (symbol? None)))

(expect (not (= (gensym) (gensym))))

(println " done")
