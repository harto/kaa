(defmacro assert (assertion)
  `(if (not ~assertion)
       (raise (py/AssertionError (str '~assertion)))))

(defmacro defun (sym params & body)
  `(def ~sym (lambda ~params ~@body)))

(defmacro do (& forms)
  `((lambda () ~@forms)))
