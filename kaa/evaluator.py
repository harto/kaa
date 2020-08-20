from itertools import chain, dropwhile, islice, repeat, takewhile
import sys

from kaa.core import is_list, is_symbol, List, Symbol


def parse_def(form):
    compiler_assert(len(form) == 3, '`def` requires 2 args', form)
    name = form[1]
    compiler_assert(is_symbol(name), '`def` name must be a symbol', form)
    val = form[2]
    return Def(name, val)


def parse_defmacro(form):
    compiler_assert(len(form) >= 3, '`defmacro` requires 2+ args', form)
    name = form[1]
    compiler_assert(is_symbol(name), 'macro name must be a symbol', name)
    params = parse_params(form[2])
    body = form[3:]
    return Def(name, Macro(params, body))


def parse_if(form):
    compiler_assert(len(form) in (3, 4), '`if` requires 2 or 3 args', form)
    return If(*form[1:])


def parse_lambda(form):
    compiler_assert(len(form) >= 2, '`lambda` requires 1+ args', form)
    params = parse_params(form[1])
    body = form[2:]
    return Lambda(params, body)


def parse_params(form):
    compiler_assert(is_list(form) and all(is_symbol(p) for p in form),
                    'params must be a list of symbols', form)
    required_names = List(sym.name for sym in _parse_required_params(form))
    optional_names = List(sym.name for sym in _parse_optional_params(form))
    rest_sym = _parse_rest_param(form)
    rest_name = rest_sym.name if rest_sym else None
    return Params(required_names, optional_names, rest_name)


def _parse_required_params(form):
    return takewhile(lambda s: s.name not in ('&optional', '&rest'), form)


def _parse_optional_params(form):
    decl = dropwhile(lambda s: s != Symbol('&optional'), form)
    return takewhile(lambda s: s.name != '&rest', islice(decl, 1, None))


def _parse_rest_param(form):
    decl = List(dropwhile(lambda s: s != Symbol('&rest'), form))
    if not decl:
        return None
    # TODO: permit &rest without name
    compiler_assert(len(decl) == 2, '`&rest` must be paired with a symbol', form)
    return decl[1]


def parse_raise(form):
    compiler_assert(len(form) == 2, '`raise` requires 1 arg', form)
    return Raise(form[1])


def parse_quote(form):
    compiler_assert(len(form) == 2, '`quote` requires 1 arg', form)
    return Quote(form[1])


def parse_try(form):
    compiler_assert(len(form) == 3, '`try` requires 2 args', form)
    expr = form[1]
    handlers = List(_parse_except_handler(except_) for except_ in form[2:])
    return Try(expr, handlers)


def _parse_except_handler(form):
    compiler_assert(is_list(form) and len(form) == 3 and form[0] == Symbol('except'),
                    'invalid except form', form)
    return form[1:3]


SPECIAL_FORMS = {
    Symbol('def'): parse_def,
    Symbol('defmacro'): parse_defmacro,
    Symbol('if'): parse_if,
    Symbol('lambda'): parse_lambda,
    Symbol('raise'): parse_raise,
    Symbol('quote'): parse_quote,
    Symbol('try'): parse_try,
}


class Def:
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, env):
        return env.define_global(self.symbol.name, evaluate(self.value, env))


class If:
    def __init__(self, cond, then, else_=None):
        self.cond = cond
        self.then = then
        self.else_ = else_

    def eval(self, env):
        if evaluate(self.cond, env):
            return evaluate(self.then, env)
        if self.else_:
            return evaluate(self.else_, env)
        return None


class Lambda:
    def __init__(self, params, body):
        self.params = params
        self.body = body
        self.lexical_env = None

    def eval(self, env):
        if self.lexical_env is None:
            # could optimise this, e.g. don't capture if no free vars
            self.lexical_env = env
        return self

    def invoke(self, args, env):
        if self.lexical_env:
            env = env.push(self.lexical_env)
        env = env.push(self.params.bind(args))
        return evaluate_all(self.body, env)


class Macro:
    def __init__(self, params, body):
        self.params = params
        self.body = body

    def expand(self, args, env):
        # FIXME: is this right? expansion shouldn't evaluate...
        return evaluate_all(self.body, env.push(self.params.bind(args)))


class Params:
    def __init__(self, required_names=(), optional_names=(), rest_name=None):
        self.required_names = required_names
        self.optional_names = optional_names
        self.rest_name = rest_name

    def bind(self, args):
        min_arity = len(self.required_names)
        max_arity = None if self.rest_name is not None else (min_arity + len(self.optional_names))
        check_arity(len(args), min_arity, max_arity)

        bindings = dict(zip(self.required_names, args))
        bindings.update(dict(zip(self.optional_names,
                                 chain(args[len(self.required_names):], repeat(None)))))
        if self.rest_name:
            num_consumed = len(self.required_names) + len(self.optional_names)
            bindings[self.rest_name] = List(args[num_consumed:])
        return bindings


class Raise:
    def __init__(self, exception):
        self.exception = exception

    def eval(self, env):
        if isinstance(self.exception, str):
            raise Exception(self.exception)
        raise evaluate(self.exception, env)


class Quote:
    def __init__(self, quoted):
        self.quoted = quoted

    def eval(self, _):
        return self.quoted


class Try:
    def __init__(self, expr, handlers):
        self.expr = expr
        self.handlers = handlers

    def eval(self, env):
        try:
            return evaluate(self.expr, env)
        except:
            ex = sys.exc_info()[1]
            for ex_type_expr, handler in self.handlers:
                ex_type = evaluate(ex_type_expr, env)
                if isinstance(ex, ex_type):
                    return evaluate(handler, env)
            raise


def check_arity(num_args, min_arity, max_arity):
    assert min_arity >= 0
    assert max_arity is None or min_arity <= max_arity

    if min_arity <= num_args and (max_arity is None or num_args <= max_arity):
        return

    if max_arity is None:
        expected = f'at least {min_arity}'
    elif min_arity == max_arity:
        expected = min_arity
    else:
        expected = f'between {min_arity} and {max_arity}'

    raise WrongArity(f'expected {expected} args, got {num_args}')


class WrongArity(Exception):
    pass


def compiler_assert(cond, msg, form):
    if not cond:
        compiler_raise(msg, form)


def compiler_raise(msg, form):
    try:
        source = ' at %s' % form.meta['source']
    except KeyError:
        source = ''
    raise CompilationError(msg + source)


class CompilationError(Exception):
    pass


def evaluate(expr, env):
    # Parse special forms
    # FIXME: this belongs in some separate compilation phase
    if is_list(expr) and expr and is_symbol(expr[0]) and expr[0] in SPECIAL_FORMS:
        parse_special_form = SPECIAL_FORMS[expr[0]]
        expr = parse_special_form(expr)

    # Function application
    if is_list(expr) and expr:
        f = evaluate(expr[0], env)
        rest = expr[1:]
        if isinstance(f, Macro):
            # FIXME: this perhaps belongs in some separate compilation phase
            expansion = f.expand(rest, env)
            return evaluate(expansion, env)
        args = List(evaluate(x, env) for x in rest)
        if isinstance(f, Lambda):
            return f.invoke(args, env)
        # assume Python callable
        return f(*args)

    # Values
    if hasattr(expr, 'eval'):
        return expr.eval(env)
    return expr


def evaluate_all(exprs, env):
    result = None
    for expr in exprs:
        result = evaluate(expr, env)
    return result
