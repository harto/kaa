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

;; closures
(def inc (let (one 1)
           (lambda (x)
             (+ one x))))
(assert (= 43 (inc 42)))
(def inc2 (let (b 1)
            (lambda (x)
              (let (c b)
                (+ c x)))))
(assert (= 4 (inc2 3)))
(def x 3)
(def get-x (lambda () x))
(def x 4)
(assert (= 4 (get-x)))

(defmacro assert (assertion)
  `(if (not ~assertion)
       (raise (py/AssertionError (str '~assertion)))))

(assert (= 1 2))
