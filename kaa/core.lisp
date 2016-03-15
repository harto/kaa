(defmacro and (& conds)
  (if conds
      `(if ~(first conds)
         (and ~@(rest conds)))
    True))

(defmacro assert (assertion)
  `(if (not ~assertion)
       (raise (py/AssertionError (str '~assertion)))))

(defmacro defun (sym params & body)
  `(def ~sym (lambda ~params ~@body)))

(defmacro do (& forms)
  `((lambda () ~@forms)))

(defmacro let (bindings & body)
  (if bindings
      (do
          ;; "let expects list of bindings as first arg"
          (assert (list? bindings))
          ;; "let expects matching pairs of key-value bindings"
          (assert (list? (first bindings)))
          (assert (= 2 (count (first bindings))))
          ;; "value must be bound to symbol"
          (assert (symbol? (first (first bindings))))
          `((lambda (~(first (first bindings)))
              (let ~(rest bindings) ~@body))
            ~(first (rest (first bindings)))))
    `(do ~@body)))
