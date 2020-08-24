import sys

from kaa.core import is_list, is_symbol
from kaa.parser import Lambda, Macro, parse


class Evaluator:
    def __init__(self, env):
        self.env = env

    def evaluate(self, expr):
        "Recursively parse and evaluate some s-expression."
        expr = parse(expr)

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
            # TODO: this perhaps belongs in some separate compilation phase?
            expansion = self.macroexpand(f, unevaled_args)
            return self.evaluate(expansion)

        evaled_args = tuple(self.evaluate(x) for x in unevaled_args)

        if isinstance(f, Lambda):
            return self.apply(f, evaled_args)

        # assume Python callable
        return f(*evaled_args)

    def macroexpand(self, macro, args):
        bindings = bind_params(macro.params, args)
        return self.with_bindings(bindings).evaluate_all(macro.body)

    def apply(self, fn, args):
        lexical_bindings = fn.lexical_env.bindings if fn.lexical_env else {}
        local_bindings = bind_params(fn.params, args)
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



def bind_params(params, args):
    check_arity(params, args)

    bindings = dict(zip(params.required, args))

    bindings.update(zip(params.optional, chain(args[len(params.required):], repeat(None))))

    if params.rest:
        num_consumed = len(params.required) + len(params.optional)
        bindings[params.rest] = List(args[num_consumed:])

    return bindings


def check_arity(params, args):
    min_arity = len(params.required)
    max_arity = None if params.rest is not None else (min_arity + len(params.optional))
    num_args = len(args)

    if min_arity <= num_args and (max_arity is None or num_args <= max_arity):
        return

    if max_arity is None:
        expected = f'at least {min_arity}'
    elif min_arity == max_arity:
        expected = min_arity
    else:
        expected = f'between {min_arity} and {max_arity}'

    # TODO: raise TypeError, like Python?
    raise WrongArity(f'expected {expected} args, got {num_args}')


class WrongArity(Exception):
    pass


class UnboundSymbol(Exception):
    def __init__(self, sym):
        try:
            msg = '%s at %s' % (sym.name, sym.meta['source'])
        except KeyError:
            msg = sym.name
        super().__init__(msg)
