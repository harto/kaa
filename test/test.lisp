(print "running test.lisp ")

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

;; lambdas
(test (= None ((lambda ()))))
(def x 5)
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
(try (do (test (= 1 2))
         (raise "fail"))
     (except py/AssertionError None))

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

(println " done")
