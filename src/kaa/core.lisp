(defmacro and (&rest conds)
  (if conds
      `(if ~(first conds)
         (and ~@(rest conds)))
    True))

(defmacro assert (assertion &optional msg)
  `(if (not ~assertion)
       (raise (py/AssertionError ~(if msg
                                      (str assertion "\n" msg)
                                    (str assertion))))))

(defmacro defun (sym params &rest body)
  `(def ~sym (lambda ~params ~@body)))

(defmacro do (&rest forms)
  `((lambda () ~@forms)))

(defmacro let (bindings &rest body)
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

(def *gensym-counter* 0)

(defun gensym (&optional prefix)
  (let ((next-value *gensym-counter*))
    (def *gensym-counter* (+ *gensym-counter* 1))
    (symbol (str (if prefix prefix "G") "__" next-value))))

(defmacro or (&rest conds)
  (if conds
      (let ((sym (gensym)))
        `(let ((~sym ~(first conds)))
           (if ~sym
               ~sym
             (or ~@(rest conds)))))))
