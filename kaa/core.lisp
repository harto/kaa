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
