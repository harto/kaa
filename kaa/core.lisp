(defmacro and (& conds)
  (if conds
      `(if ~(first conds)
         (and ~@(rest conds)))
    True))

(defmacro assert (assertion & msg)
  `(if (not ~assertion)
       (raise (py/AssertionError ~(if msg
                                      (str assertion "\n" (first msg))
                                    (str assertion))))))

(defmacro defun (sym params & body)
  `(def ~sym (lambda ~params ~@body)))

(defmacro do (& forms)
  `((lambda () ~@forms)))

(defmacro let (bindings & body)
  (if bindings
      (do
          (assert (list? bindings)
                  "let expects list of bindings as first arg")
          (assert (and (list? (first bindings))
                       (= 2 (count (first bindings))))
                  "let binding pairs must be 2-element lists")
          (assert (symbol? (first (first bindings)))
                  "value must be bound to symbol")
          `((lambda (~(first (first bindings)))
              (let ~(rest bindings) ~@body))
            ~(first (rest (first bindings)))))
    `(do ~@body)))
