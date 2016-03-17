;; multi-line expressions
(assert (= 21
           (* (+ 1 2)
              (+ 3 4))))

;; def
(def foo 42)
(def bar (* 3 foo))
(assert (= 126 bar))

;; lambdas
(def x 5)
(def add (lambda (x y)
           (+ x y)))
(assert (= 3 (add 1 2)))
(assert (= 5 x))

;; let
(def x 1)
(def y 42)
(let ((x 2))
  (let ((x y))
    (assert (= y x)))
  (assert (= 2 x)))
(assert (= 1 x))

;; closures
(def inc (let ((one 1))
           (lambda (x)
             (+ one x))))
(assert (= 43 (inc 42)))
(def inc2 (let ((b 1))
            (lambda (x)
              (let ((c b))
                (+ c x)))))
(assert (= 4 (inc2 3)))
(def x 3)
(defun get-x () x)
(def x 4)
(assert (= 4 (get-x)))

;; unquoting / splicing
;; (let (x '(b c d))
;;   (assert (= '(a (b c d) e)
;;              `(a ~x e)))
;;   (assert (= '(a b c d e)
;;              `(a ~@x e))))

;; try/raise/except
(try (do (assert (= 1 2))
         (raise "fail"))
     (except py/AssertionError None))

;; conditionals
(assert (= "ok" (if True "ok" "fail")))
(assert (= None (if False "fail")))

(assert (and))
(assert (and "foo"))
(assert (and 1 2))
(assert (not (and False "foo")))
(assert (not (and None (raise "shouldn't get here"))))

(assert (not (or)))
(assert (= "foo" (or "foo")))
(assert (= "bar" (or False "bar" (raise "shouldn't get here"))))
