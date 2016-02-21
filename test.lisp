(assert (= 21
           (* (+ 1 2)
              (+ 3 4))))

(def foo 42)
(def bar (* 3 foo))
(assert (= 126 bar))
