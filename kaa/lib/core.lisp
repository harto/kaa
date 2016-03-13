(defmacro assert (assertion)
  `(if (not ~assertion)
       (raise (py/AssertionError (str '~assertion)))))

(defmacro do (& forms)
  `((lambda () ~@forms)))
