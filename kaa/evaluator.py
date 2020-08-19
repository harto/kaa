from kaa.core import List, Symbol


# FIXME: figure out where to put this
def evaluate(expr, env):
    # FIXME: this belongs in some compilation phase, not eval
    expr = maybe_eval_special_form(expr)

    if isinstance(expr, List) and expr:
        return invoke(expr, env)
    if hasattr(expr, 'eval'):
        return expr.eval(env)
    # native Python type
    return expr


def invoke(form, env):
    first = evaluate(form[0], env)
    rest = form[1:]

    if isinstance(first, Macro):
        expansion = first(env, *rest)
        return evaluate(expansion, env)

    args = [evaluate(expr, env) for expr in rest]
    if isinstance(first, Lambda):
        return first(env, *args)

    # assume Python callable
    return first(*args)


def maybe_eval_special_form(expr):
    if not (isinstance(expr, List) and len(expr) and isinstance(expr[0], Symbol)):
        return expr

    handlers = {Symbol('def'): Def.parse,
                Symbol('defmacro'): Macro.define,
                Symbol('if'): If.parse,
                Symbol('lambda'): Lambda.parse,
                Symbol('raise'): Raise.parse,
                Symbol('quote'): Quote.parse,
                Symbol('try'): Try.parse}
    try:
        handler = handlers[expr[0]]
    except KeyError:
        return expr
    return handler(expr)


# FIXME: these are here because of a circular dependency
from kaa.special_forms import Def, Macro, If, Lambda, Raise, Quote, Try  # pylint: disable=cyclic-import,wrong-import-position
