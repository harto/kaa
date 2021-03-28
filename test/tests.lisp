(print "tests.lisp ")

;; (import (expect expect-raises) from kaa.test)

;; (assert expect)
;; (assert expect-raises)

;; (import kaa.test as t)
;; (import .other as o)

;; (expect-raises py/AssertionError (expect (= 1 2)))

;; (assert (= 5 (+ 2 2)))
(defmacro test (expr)
  `(do
    (assert ~expr)
    (print ".")))

;; multi-line expressions
(test (= 21
         (* (+ 1 2)
            (+ 3 4))))

;; with blank lines
(test (= 3
         (+ 1

            1

   ;; hi

            1)))

;; def
(def foo 42)
(def bar (* 3 foo))
(test (= 126 bar))

;; quoting
(test (symbol? 'some-symbol))
(test (= (list 'a 'b 'c) '(a b c)))
(test (list? ()))
(test (empty? ()))

;; lambdas
(test (= None ((lambda ()))))
(test (= 3 ((lambda () 3))))
(test (= 4 ((lambda (x) x) 4)))
(def x 5)
(test (= 5 ((lambda () x))))
(def add (lambda (x y)
           (+ x y)))
(test (= 3 (add 1 2)))
(test (= 5 x))

;; let
(def x 1)
(def y 42)
(let ())
(let ((x 2))
  (let ((x y))
    (test (= y x)))
  (test (= 2 x)))
(test (= 1 x))

;; closures
(def inc (let ((one 1))
           (lambda (x)
             (+ one x))))
(test (= 43 (inc 42)))
(def inc2 (let ((b 1))
            (lambda (x)
              (let ((c b))
                (+ c x)))))
(test (= 4 (inc2 3)))
(def x 3)
(defun get-x () x)
(def x 4)
(test (= 4 (get-x)))

;; unquoting / splicing
(let ((x '(b c d)))
  (test (= '(a (b c d) e)
           `(a ~x e)))
  (test (= '(a b c d e)
           `(a ~@x e))))

;; try/raise/except
(test (= 'ok (try (do (assert (= 1 2))
                      (raise "fail"))
                  (except py/AssertionError 'ok))))

(test (= 'ok (try (raise (/ 1 0))
                  (except py/ValueError (raise "unreachable"))
                  (except py/ZeroDivisionError 'ok)
                  (except py/Exception (raise "unreachable")))))

;; conditionals
(test (= 'ok (if True 'ok 'fail)))
(test (= None (if False 'fail)))

(test (and))
(test (and "foo"))
(test (and 'bar))
(test (and 1 2))
(test (not (and False "foo")))
(test (not (and None (raise "should be unreachable"))))

(test (not (or)))
(test (= "foo" (or "foo")))
(test (= "bar" (or False "bar" (raise "should be unreachable"))))

(test (not (= (gensym) (gensym))))

;; macroexpansion
;; (defmacro m1 ()
;;   )
;; (defmacro m2 ()
;;   )

(println " done")
