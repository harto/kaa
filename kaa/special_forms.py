from kaa.core import is_list, is_symbol, List, Symbol
import itertools
import sys

def eval_all(exprs, ns):
    result = None
    for e in exprs:
        result = eval(e, ns)
    return result

class Def(object):

    @classmethod
    def parse(cls, L):
        if len(L) != 3:
            _err('wrong number of args to def', L)
        sym = L[1]
        if not is_symbol(sym):
            _err('first arg to def must be symbol', L)
        val = L[2]
        return cls(sym, val)

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        return ns.define_global(self.symbol.name, eval(self.value, ns))

class If(object):

    @classmethod
    def parse(cls, L):
        if len(L) not in (3, 4):
            _err('wrong number of args to if', L)
        return cls(*L[1:])

    def __init__(self, cond, then, else_ = None):
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
    def parse(cls, L):
        if len(L) < 2:
            _err('missing params list', L)
        params = Params.parse(L[1])
        body = L[2:]
        return cls(params, body)

    def __init__(self, params, body):
        self.params = params
        self.body = body
        self.lexical_bindings = None

    def __call__(self, ns, *args):
        if self.lexical_bindings:
            ns = ns.push(self.lexical_bindings)
        ns = ns.push(self.params.bind(args))
        return eval_all(self.body, ns)

    def eval(self, ns):
        if self.lexical_bindings is None:
            # could optimise this, e.g. don't capture if no free vars
            self.lexical_bindings = ns
        return self

class Params(object):

    @classmethod
    def parse(cls, L):
        if not (is_list(L) and all(is_symbol(p) for p in L)):
            _err('params must be list of symbols', L)
        required_names = [sym.name for sym in cls._parse_required(L)]
        optional_names = [sym.name for sym in cls._parse_optional(L)]
        rest = cls._parse_rest(L)
        rest_name = rest and rest.name or None
        return cls(required_names, optional_names, rest_name)

    @classmethod
    def _parse_required(cls, L):
        return list(itertools.takewhile(lambda s: not s.name.startswith('&'), L))

    @classmethod
    def _parse_optional(cls, L):
        decl = list(itertools.dropwhile(lambda s: s != Symbol('&optional'), L))
        return list(itertools.takewhile(lambda s: not s.name.startswith('&'), decl[1:]))

    @classmethod
    def _parse_rest(cls, L):
        decl = list(itertools.dropwhile(lambda s: s != Symbol('&rest'), L))
        if len(decl) not in (0, 2):
            _err('invalid rest declaration', L)
        try:
            return decl[1]
        except IndexError:
            return None

    def __init__(self, required_names = [], optional_names = [], rest_name = None):
        self.required_names = required_names
        self.optional_names = optional_names
        self.rest_name = rest_name
        self.min_arity = len(required_names)
        self.max_arity = (rest_name is not None
                          and float('inf')
                          or (self.min_arity + len(optional_names)))

    def bind(self, args):
        self._check_arity(args)
        bound = dict(zip([name for name in self.required_names], args))
        bound.update(dict(zip([name for name in self.optional_names],
                              itertools.chain(args[len(self.required_names):],
                                              itertools.repeat(None)))))
        if self.rest_name:
            num_consumed = len(self.required_names) + len(self.optional_names)
            bound[self.rest_name] = List(args[num_consumed:])
        return bound

    def _describe_arity(self):
        if self.max_arity == float('inf'):
            return '%d or more' % self.min_arity
        elif self.min_arity != self.max_arity:
            return 'between %d and %d' % (self.min_arity, self.max_arity)
        else:
            return str(self.min_arity)

    def _check_arity(self, args):
        received = len(args)
        if received < self.min_arity or self.max_arity < received:
            raise ArityException('expected %s args, got %d' %
                                 (self._describe_arity(), received))

class Macro(object):

    @classmethod
    def define(cls, L):
        if len(L) < 3:
            _err('wrong number of args to defmacro', L)
        name = L[1]
        if not is_symbol(name):
            _err('invalid macro name', name)
        params = Params.parse(L[2])
        body = L[3:]
        return Def(name, cls(params, body))

    def __init__(self, params, body):
        self.params = params
        self.body = body

    def __call__(self, ns, *args):
        return eval_all(self.body, ns.push(self.params.bind(args)))

class Raise(object):

    @classmethod
    def parse(cls, L):
        try:
            exception = L[1]
        except IndexError:
            _err('raise takes one arg', L)
        return cls(exception)

    def __init__(self, exception):
        self.exception = exception

    def eval(self, ns):
        if isinstance(self.exception, str):
            raise Exception(self.exception)
        else:
            raise eval(self.exception, ns)

class Quote(object):

    @classmethod
    def parse(cls, L):
        if len(L) != 2:
            _err('quote takes one arg', L)
        return cls(L[1])

    def __init__(self, quoted):
        self.quoted = quoted

    def eval(self, _):
        return self.quoted

class Try(object):

    @classmethod
    def parse(cls, L):
        if len(L) != 3:
            _err('invalid try-except form', L)
        expr = L[1]
        handlers = [cls._parse_handler(except_) for except_ in L[2:]]
        return cls(expr, handlers)

    @classmethod
    def _parse_handler(cls, L):
        if not (is_list(L) and len(L) == 3 and L[0] == Symbol('except')):
            _err('invalid except form', L)
        return L[1:3]

    def __init__(self, expr, handlers):
        self.expr = expr
        self.handlers = handlers

    def eval(self, ns):
        try:
            return eval(self.expr, ns)
        except:
            ex = sys.exc_info()[1]
            for ex_type_expr, handler in self.handlers:
                ex_type = eval(ex_type_expr, ns)
                if isinstance(ex, ex_type):
                    return eval(handler, ns)
            raise

def _err(msg, obj = None):
    if obj:
        msg += ' at %s' % obj.source_meta
    raise CompilationException(msg)

class ArityException(Exception): pass
class CompilationException(Exception): pass

from kaa.evaluator import eval
