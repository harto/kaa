from collections import namedtuple
from itertools import chain, dropwhile, islice, repeat, takewhile
import sys

from kaa.core import is_list, is_symbol, List, Symbol


def parse_def(form):
    compiler_assert(len(form) == 3, '`def` requires 2 args', form)
    name, val = form[1:]
    compiler_assert(is_symbol(name), '`def` name must be a symbol', form)
    return Def(name, val)


def parse_defmacro(form):
    compiler_assert(len(form) >= 3, '`defmacro` requires 2+ args', form)
    name, params, *body = form[1:]
    compiler_assert(is_symbol(name), 'macro name must be a symbol', name)
    return Def(name, Macro(parse_params(params), body))


def parse_if(form):
    compiler_assert(len(form) in (3, 4), '`if` requires 2 or 3 args', form)
    return If(form[1], form[2], form[3] if len(form) == 4 else None)


def parse_lambda(form):
    compiler_assert(len(form) >= 2, '`lambda` requires 1+ args', form)
    params, *body = form[1:]
    return Lambda(parse_params(params), body, None)


def parse_params(form):
    compiler_assert(is_list(form) and all(is_symbol(p) for p in form),
                    'params must be a list of symbols', form)
    required_names = tuple(sym.name for sym in _parse_required_params(form))
    optional_names = tuple(sym.name for sym in _parse_optional_params(form))
    rest_sym = _parse_rest_param(form)
    rest_name = rest_sym.name if rest_sym else None
    return Params(required_names, optional_names, rest_name)


def _parse_required_params(form):
    return takewhile(lambda s: s.name not in ('&optional', '&rest'), form)


def _parse_optional_params(form):
    decl = dropwhile(lambda s: s != Symbol('&optional'), form)
    return takewhile(lambda s: s.name != '&rest', islice(decl, 1, None))


def _parse_rest_param(form):
    decl = tuple(dropwhile(lambda s: s != Symbol('&rest'), form))
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
    compiler_assert(len(form) >= 3, '`try` requires 2+ args', form)
    expr, *excepts = form[1:]
    return Try(expr, (_parse_except(except_) for except_ in excepts))


def _parse_except(form):
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


Def = namedtuple('Def', 'symbol value')
If = namedtuple('If', 'cond then else_')
Lambda = namedtuple('Lambda', 'params body lexical_env')
Macro = namedtuple('Macro', 'params body')
Quote = namedtuple('Quote', 'value')
Raise = namedtuple('Raise', 'ex')
Try = namedtuple('Try', 'expr handlers')


class Params:
    def __init__(self, required_names, optional_names, rest_name):
        self.required_names = required_names
        self.optional_names = optional_names
        self.rest_name = rest_name

    def check_arity(self, args):
        min_arity = len(self.required_names)
        max_arity = None if self.rest_name is not None else (min_arity + len(self.optional_names))
        num_args = len(args)

        if min_arity <= num_args and (max_arity is None or num_args <= max_arity):
            return

        if max_arity is None:
            expected = f'at least {min_arity}'
        elif min_arity == max_arity:
            expected = min_arity
        else:
            expected = f'between {min_arity} and {max_arity}'

        raise WrongArity(f'expected {expected} args, got {num_args}')

    def bind(self, args):
        self.check_arity(args)

        bindings = dict(zip(self.required_names, args))

        bindings.update(dict(zip(self.optional_names,
                                 chain(args[len(self.required_names):], repeat(None)))))

        if self.rest_name:
            num_consumed = len(self.required_names) + len(self.optional_names)
            bindings[self.rest_name] = List(args[num_consumed:])

        return bindings


class WrongArity(Exception):
    pass


def compiler_assert(cond, msg, form):
    if cond:
        return
    try:
        source = ' at %s' % form.meta['source']
    except KeyError:
        source = ''
    raise CompilationError(msg + source)


class CompilationError(Exception):
    pass


def is_special_form(expr):
    return is_list(expr) and expr and is_symbol(expr[0]) and expr[0] in SPECIAL_FORMS


def parse_special_form(expr):
    sym = expr[0]
    parse = SPECIAL_FORMS[sym]
    return parse(expr)


class Evaluator:
    def __init__(self, env):
        self.env = env

    def evaluate(self, expr):
        "Recursively parse and evaluate some s-expression."
        # TODO: does this perhaps belong in some separate compilation phase?
        if is_special_form(expr):
            expr = parse_special_form(expr)

        # Function invocation
        if is_list(expr) and expr:
            return self.invoke(expr)

        evaluator = getattr(self, f'eval__{type(expr).__name__}', None)
        if evaluator:
            return evaluator(expr)

        return expr

    def evaluate_all(self, exprs):
        "Evaluate a sequence of expressions, returning the result of the last one."
        result = None
        for expr in exprs:
            result = self.evaluate(expr)
        return result

    def invoke(self, expr):
        f = self.evaluate(expr[0])
        unevaled_args = expr[1:]

        if isinstance(f, Macro):
            # TODO: this perhaps belongs in some separate compilation phase
            expansion = self.macroexpand(f, unevaled_args)
            return self.evaluate(expansion)

        evaled_args = tuple(self.evaluate(x) for x in unevaled_args)

        if isinstance(f, Lambda):
            return self.apply(f, evaled_args)

        # assume Python callable
        return f(*evaled_args)

    def macroexpand(self, macro, args):
        bindings = macro.params.bind(args)
        return self.with_bindings(bindings).evaluate_all(macro.body)

    def apply(self, fn, args):
        lexical_bindings = fn.lexical_env.bindings if fn.lexical_env else {}
        local_bindings = fn.params.bind(args)
        bindings = dict(**lexical_bindings)
        bindings.update(local_bindings)
        return self.with_bindings(bindings).evaluate_all(fn.body)

    def with_bindings(self, bindings):
        return Evaluator(self.env.push(bindings))

    def eval__Def(self, node):  # pylint: disable=invalid-name
        val = self.evaluate(node.value)
        self.env.define_global(node.symbol.name, val)
        return val

    def eval__If(self, node):  # pylint: disable=invalid-name
        if self.evaluate(node.cond):
            return self.evaluate(node.then)
        return self.evaluate(node.else_)

    def eval__Lambda(self, node):  # pylint: disable=invalid-name
        # TODO: this seems a bit hacky. Should we be capturing the lexical env elsewhere?
        if node.lexical_env is None:
            # could optimise this, e.g. don't capture if no free vars
            return Lambda(node.params, node.body, self.env)
        return node

    def eval__Quote(self, node):  # pylint: disable=invalid-name, no-self-use
        return node.value

    def eval__Raise(self, node):  # pylint: disable=invalid-name
        ex = self.evaluate(node.ex)
        if isinstance(ex, str):
            raise RuntimeError(ex)
        raise ex

    def eval__Symbol(self, sym):  # pylint: disable=invalid-name
        try:
            return self.env[sym.name]
        except KeyError:
            raise UnboundSymbol(sym)

    def eval__Try(self, node):  # pylint: disable=invalid-name
        try:
            return self.evaluate(node.expr)
        except:
            ex = sys.exc_info()[1]
            for ex_type_expr, handler in node.handlers:
                ex_type = self.evaluate(ex_type_expr)
                if isinstance(ex, ex_type):
                    return self.evaluate(handler)
            raise


class UnboundSymbol(Exception):
    def __init__(self, sym):
        try:
            msg = '%s at %s' % (sym.name, sym.meta['source'])
        except KeyError:
            msg = sym.name
        super().__init__(msg)
