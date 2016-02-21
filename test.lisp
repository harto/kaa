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
(let (x 2)
  (let (x y)
    (assert (= y x)))
  (assert (= 2 x)))
(assert (= 1 x))

;(assert (= 1 2))
