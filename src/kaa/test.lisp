;; kaa.test
;; Testing helpers

(defmacro expect (cond)
  `(assert ~cond))

(defmacro expect-raises (ex expr)
  (let ((expected-failure (gensym)))
    `(assert (= '~expected-failure (try ~expr (except ~ex '~expected-failure)))
             (str ex " not raised"))))
