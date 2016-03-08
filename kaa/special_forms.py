from kaa.types import Namespace, List, Symbol

def eval_all(exprs, ns):
    result = None
    for e in exprs:
        result = eval(e, ns)
        return result

class Def(object):

    @classmethod
    def create(cls, L):
        try:
            sym, val = L[1:]
        except ValueError:
            sym = val = None
        if not _is_symbol(sym):
            _err('invalid def form', L.source_meta)
        return cls(sym, val)

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        result = ns[self.symbol.name] = eval(self.value, ns)
        return result

class If(object):

    @classmethod
    def create(cls, L):
        if len(L) not in (3, 4):
            _err('invalid if form', L.source_meta)
        cond = L[1]
        then = L[2]
        try:
            else_ = L[3]
        except IndexError:
            else_ = None
        return cls(cond, then, else_)

    def __init__(self, cond, then, else_):
        self.cond = cond
        self.then = then
        self.else_ = else_

    def eval(self, ns):
        if eval(self.cond, ns):
            return eval(self.then, ns)
        elif self.else_:
            return eval(self.else_, ns)
        else:
            return None

class Lambda(object):

    @classmethod
    def create(cls, L):
        try:
            params = L[1]
        except IndexError:
            params = None
        if not _is_valid_param_list(params):
            _err('invalid lambda params', L.source_meta)
        body = L[2:]
        return cls([p.name for p in params], body)

    def __init__(self, param_names, body):
        self.param_names = param_names
        self.body = body
        self.lexical_bindings = None

    def __call__(self, ns, *args):
        self._check_arity(args)
        if self.lexical_bindings:
            ns = Namespace(bindings=self.lexical_bindings,
                           parent=ns)
        ns = Namespace(bindings=dict(zip(self.param_names, args)),
                       parent=ns)
        return eval_all(self.body, ns)

    def _check_arity(self, args):
        _check_arity(self.param_names, args)

    def eval(self, ns):
        if self.lexical_bindings is None:
            # could optimise this, e.g. don't capture if no free vars
            self.lexical_bindings = ns
        return self

# todo: replace with macro
class Let(object):

    @classmethod
    def create(cls, L):
        try:
            first = L[1]
        except IndexError:
            first = None
        rest = L[2:]
        bindings = cls._parse_bindings(first)
        return cls(bindings, rest)

    @classmethod
    def _parse_bindings(cls, bindings):
        if not isinstance(bindings, List):
            _err('let expects list of bindings as first arg', bindings.source_meta)
        if len(bindings) % 2:
            _err('let expects matching pairs of key-value bindings', bindings.source_meta)
        pairs = zip(*(iter(bindings),) * 2)
        bindings = []
        for sym, val in pairs:
            if not _is_symbol(sym):
                _err('value must be bound to symbol', bindings.source_meta)
            bindings.append((sym.name, val))
        return bindings

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, ns):
        return eval_all(self.body, self.with_bindings(ns))

    def with_bindings(self, ns):
        ns = Namespace(parent=ns)
        for name, expr in self.bindings:
            ns[name] = eval(expr, ns)
        return ns

class Macro(object):

    @classmethod
    def define(cls, L):
        try:
            name = L[1]
            params = L[2]
        except IndexError:
            name = params = None
        if not _is_symbol(name):
            _err('invalid macro name', L.source_meta)
        if not _is_valid_param_list(params):
            _err('invalid macro params', L.source_meta)
        body = L[3:]
        return Def(name, cls(params, body))

    def __init__(self, params, body):
        self.params = params
        self.body = body

    def __call__(self, ns, *args):
        _check_arity(self.params, args)
        ns = Namespace(bindings=self._locals(args), parent=ns)
        return eval_all(self.body, ns)

    def _locals(self, args):
        return dict(zip([sym.name for sym in self.params], args))

class Raise(object):

    @classmethod
    def create(cls, L):
        try:
            exception = L[1]
        except IndexError:
            _err('raise takes one arg', L.source_meta)
        return cls(exception)

    def __init__(self, exception):
        self.exception = exception

    def eval(self, ns):
        if isinstance(self.exception, str):
            raise Exception(self.exception)
        else:
            raise eval(self.exception, ns)

class Quasiquote(object):

    @classmethod
    def create(cls, L):
        if len(L) != 2:
            _err('quasiquote takes one arg', L.source_meta)
        return cls(L[1])

    def __init__(self, quoted):
        self.quoted = quoted

    def eval(self, ns):
        return self.eval_unquotes(self.quoted, ns)

    def eval_unquotes(self, expr, ns):
        if not (isinstance(expr, List) and len(expr)):
            return expr
        first = expr[0]
        if first == Symbol('unquote'):
            if len(expr) != 2:
                _err('unquote takes one arg', expr.source_meta)
            second = expr[1]
            return eval(second, ns)
        else:
            return List([self.eval_unquotes(e, ns) for e in expr])

class Quote(object):

    @classmethod
    def create(cls, L):
        if len(L) != 2:
            _err('quote takes one arg', L.source_meta)
        return cls(L[1])

    def __init__(self, quoted):
        self.quoted = quoted

    def eval(self, _):
        return self.quoted

def _is_symbol(x):
    return isinstance(x, Symbol)

def _is_valid_param_list(params):
    return isinstance(params, List) and all(_is_symbol(p) for p in params)

def _check_arity(params, args):
    num_expected = len(params)
    num_received = len(args)
    if num_received != num_expected:
        raise ArityException('expected %d args, got %d' % (num_expected,
                                                           num_received))
def _err(msg, source_meta):
    if source_meta:
        msg += ' (%s)' % source_meta
    raise CompilationException(msg)

class ArityException(Exception): pass
class CompilationException(Exception): pass

from kaa.evaluator import eval
