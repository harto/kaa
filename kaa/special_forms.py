import itertools
import sys

from kaa.core import is_list, is_symbol, List, Symbol


def eval_all(exprs, ns):
    result = None
    for expr in exprs:
        result = evaluate(expr, ns)
    return result


class Def:
    @classmethod
    def parse(cls, form):
        if len(form) != 3:
            _err('wrong number of args to def', form)
        sym = form[1]
        if not is_symbol(sym):
            _err('first arg to def must be symbol', form)
        val = form[2]
        return cls(sym, val)

    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, ns):
        return ns.define_global(self.symbol.name, evaluate(self.value, ns))


class If:
    @classmethod
    def parse(cls, form):
        if len(form) not in (3, 4):
            _err('wrong number of args to if', form)
        return cls(*form[1:])

    def __init__(self, cond, then, else_=None):
        self.cond = cond
        self.then = then
        self.else_ = else_

    def eval(self, ns):
        if evaluate(self.cond, ns):
            return evaluate(self.then, ns)
        if self.else_:
            return evaluate(self.else_, ns)
        return None


class Lambda:
    @classmethod
    def parse(cls, form):
        if len(form) < 2:
            _err('missing params list', form)
        params = Params.parse(form[1])
        body = form[2:]
        return cls(params, body)

    def __init__(self, params, body):
        self.params = params
        self.body = body
        self.lexical_env = None

    def __call__(self, ns, *args):
        if self.lexical_env:
            ns = ns.push(self.lexical_env)
        ns = ns.push(self.params.bind(args))
        return eval_all(self.body, ns)

    def eval(self, ns):
        if self.lexical_env is None:
            # could optimise this, e.g. don't capture if no free vars
            self.lexical_env = ns
        return self


class Params:
    @classmethod
    def parse(cls, form):
        if not (is_list(form) and all(is_symbol(p) for p in form)):
            _err('params must be list of symbols', form)
        required_names = [sym.name for sym in cls._parse_required(form)]
        optional_names = [sym.name for sym in cls._parse_optional(form)]
        rest = cls._parse_rest(form)
        rest_name = rest.name if rest else None
        return cls(required_names, optional_names, rest_name)

    @classmethod
    def _parse_required(cls, form):
        return list(itertools.takewhile(lambda s: not s.name.startswith('&'), form))

    @classmethod
    def _parse_optional(cls, form):
        decl = list(itertools.dropwhile(lambda s: s != Symbol('&optional'), form))
        return list(itertools.takewhile(lambda s: not s.name.startswith('&'), decl[1:]))

    @classmethod
    def _parse_rest(cls, form):
        decl = list(itertools.dropwhile(lambda s: s != Symbol('&rest'), form))
        if len(decl) not in (0, 2):
            _err('invalid rest declaration', form)
        try:
            return decl[1]
        except IndexError:
            return None

    def __init__(self, required_names=None, optional_names=None, rest_name=None):
        self.required_names = required_names or []
        self.optional_names = optional_names or []
        self.rest_name = rest_name
        self.min_arity = len(required_names)
        self.max_arity = float('inf') if rest_name is not None \
            else (self.min_arity + len(optional_names))

    def bind(self, args):
        self._check_arity(args)
        bound = dict(zip(self.required_names, args))
        bound.update(dict(zip(self.optional_names,
                              itertools.chain(args[len(self.required_names):],
                                              itertools.repeat(None)))))
        if self.rest_name:
            num_consumed = len(self.required_names) + len(self.optional_names)
            bound[self.rest_name] = List(args[num_consumed:])
        return bound

    def _describe_arity(self):
        if self.max_arity == float('inf'):
            return '%d or more' % self.min_arity
        if self.min_arity != self.max_arity:
            return 'between %d and %d' % (self.min_arity, self.max_arity)
        return str(self.min_arity)

    def _check_arity(self, args):
        received = len(args)
        if received < self.min_arity or self.max_arity < received:
            raise ArityException('expected %s args, got %d' %
                                 (self._describe_arity(), received))


class Macro:
    @classmethod
    def define(cls, form):
        if len(form) < 3:
            _err('wrong number of args to defmacro', form)
        name = form[1]
        if not is_symbol(name):
            _err('invalid macro name', name)
        params = Params.parse(form[2])
        body = form[3:]
        return Def(name, cls(params, body))

    def __init__(self, params, body):
        self.params = params
        self.body = body

    def __call__(self, ns, *args):
        return eval_all(self.body, ns.push(self.params.bind(args)))


class Raise:
    @classmethod
    def parse(cls, form):
        try:
            exception = form[1]
        except IndexError:
            _err('raise takes one arg', form)
        return cls(exception)

    def __init__(self, exception):
        self.exception = exception

    def eval(self, ns):
        if isinstance(self.exception, str):
            raise Exception(self.exception)
        raise evaluate(self.exception, ns)


class Quote:
    @classmethod
    def parse(cls, form):
        if len(form) != 2:
            _err('quote takes one arg', form)
        return cls(form[1])

    def __init__(self, quoted):
        self.quoted = quoted

    def eval(self, _):
        return self.quoted


class Try:
    @classmethod
    def parse(cls, form):
        if len(form) != 3:
            _err('invalid try-except form', form)
        expr = form[1]
        handlers = [cls._parse_handler(except_) for except_ in form[2:]]
        return cls(expr, handlers)

    @classmethod
    def _parse_handler(cls, form):
        if not (is_list(form) and len(form) == 3 and form[0] == Symbol('except')):
            _err('invalid except form', form)
        return form[1:3]

    def __init__(self, expr, handlers):
        self.expr = expr
        self.handlers = handlers

    def eval(self, ns):
        try:
            return evaluate(self.expr, ns)
        except:
            ex = sys.exc_info()[1]
            for ex_type_expr, handler in self.handlers:
                ex_type = evaluate(ex_type_expr, ns)
                if isinstance(ex, ex_type):
                    return evaluate(handler, ns)
            raise


def _err(msg, obj=None):
    try:
        msg += ' at %s' % obj.meta['source']
    except KeyError:
        pass
    raise CompilationException(msg)


class ArityException(Exception):
    pass


class CompilationException(Exception):
    pass


# FIXME: this is here because of a circular dependency
from kaa.evaluator import evaluate  # pylint: disable=wrong-import-position
