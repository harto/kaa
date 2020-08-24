from collections import namedtuple
from itertools import dropwhile, islice, takewhile

from kaa.core import is_list, is_symbol, Symbol


def parse(expr):
    if is_list(expr) and expr and is_symbol(expr[0]):
        try:
            f = SPECIAL_FORMS[expr[0]]
        except KeyError:
            pass
        else:
            expr = f(expr)
    return expr


Def = namedtuple('Def', 'symbol value')
If = namedtuple('If', 'cond then else_')
Lambda = namedtuple('Lambda', 'params body lexical_env')
Macro = namedtuple('Macro', 'params body')
Params = namedtuple('Params', 'required_names optional_names rest_name')
Quote = namedtuple('Quote', 'value')
Raise = namedtuple('Raise', 'ex')
Try = namedtuple('Try', 'expr handlers')


# (def NAME EXPR)
def parse_def(form):
    check(len(form) == 3, '`def` requires 2 args', form)
    _, name, val = form
    check(is_symbol(name), '`def` name must be a symbol', form)
    return Def(name, val)


# (defmacro NAME PARAMS [EXPR …])
def parse_defmacro(form):
    check(len(form) >= 3, '`defmacro` requires 2+ args', form)
    _, name, params, *body = form
    check(is_symbol(name), 'macro name must be a symbol', name)
    return Def(name, Macro(parse_params(params), body))


# (if COND THEN [ELSE])
def parse_if(form):
    check(len(form) in (3, 4), '`if` requires 2 or 3 args', form)
    return If(form[1], form[2], form[3] if len(form) == 4 else None)


# (lambda PARAMS [EXPR …])
def parse_lambda(form):
    check(len(form) >= 2, '`lambda` requires 1+ args', form)
    _, params, *body = form
    return Lambda(parse_params(params), body, None)


# ([SYM …] [&optional SYM …] [&rest SYM])
def parse_params(form):
    check(is_list(form) and all(is_symbol(p) for p in form),
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
    check(len(decl) == 2, '`&rest` must be paired with a symbol', form)
    return decl[1]


# (raise EXPR)
def parse_raise(form):
    check(len(form) == 2, '`raise` requires 1 arg', form)
    return Raise(form[1])


# (quote EXPR)
def parse_quote(form):
    check(len(form) == 2, '`quote` requires 1 arg', form)
    return Quote(form[1])


# (try EXPR (catch EX EXPR) …)
def parse_try(form):
    check(len(form) >= 3, '`try` requires 2+ args', form)
    _, expr, *excepts = form
    return Try(expr, (_parse_except(except_) for except_ in excepts))


def _parse_except(form):
    check(is_list(form) and len(form) == 3 and form[0] == Symbol('except'),
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


def check(cond, msg, form):
    if cond:
        return
    try:
        source = ' at %s' % form.meta['source']
    except KeyError:
        source = ''
    raise ParseError(msg + source)


class ParseError(Exception):
    pass
