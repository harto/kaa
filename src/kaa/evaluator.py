import sys
from itertools import chain, repeat

from kaa.core import is_list, is_symbol, List
from kaa.parser import Lambda, Macro, parse


class Evaluator:
    def __init__(self, ns, env=None):
        self.ns = ns
        self.env = ns.defs if env is None else env

    def evaluate(self, expr):
        "Recursively parse and evaluate some s-expression."
        expr = parse(expr)

        # Function invocation
        if is_list(expr) and expr:
            return self.call(expr)

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

    def call(self, expr):
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
        bindings = {}
        bindings.update(fn.lexical_env.bindings)
        bindings.update(bind_params(fn.params, args))
        return Evaluator(fn.ns, self.env.push_bindings(bindings)).evaluate_all(fn.body)

    def with_bindings(self, bindings):
        return Evaluator(self.ns, self.env.push_bindings(bindings))

    def eval__Def(self, node):  # pylint: disable=invalid-name
        val = self.evaluate(node.value)
        self.ns[node.symbol] = val
        return val

    def eval__If(self, node):  # pylint: disable=invalid-name
        if self.evaluate(node.cond):
            return self.evaluate(node.then)
        return self.evaluate(node.else_)

    def eval__Import(self, node):  # pylint: disable=invalid-name
        symbols = '*' if is_symbol(node.names) and node.names.name == '*' \
            else tuple(sym.name for sym in node.names) if is_list(node.names) \
            else ()
        alias = node.alias.name if node.alias else None
        if node.source.ns == 'py':
            self.ns.import_module(self.ns.load_module(node.source.name), symbols, alias)
        else:
            self.ns.import_ns(self.ns.load_ns(node.source.name), symbols, alias)

    def eval__Lambda(self, node):  # pylint: disable=invalid-name
        if not node.ns:
            # The first time the lambda is taken as a value, capture:
            # - its ns, in case of side-effects in body, e.g. `(def …)`
            # - its lexical bindings
            # TODO: could optimise this, e.g. only capture free vars
            return Lambda(node.params, node.body, self.ns, self.env)
        return node

    def eval__Quote(self, node):  # pylint: disable=invalid-name, no-self-use
        return node.value

    def eval__Raise(self, node):  # pylint: disable=invalid-name
        ex = self.evaluate(node.ex)
        if isinstance(ex, str):
            raise RuntimeError(ex)
        raise ex

    def eval__Symbol(self, sym):  # pylint: disable=invalid-name
        if sym.ns == 'py':
            return eval(sym.name) # pylint: disable=eval-used
        for env in (self.env, self.ns):
            try:
                return env[sym]
            except KeyError:
                pass
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

    raise WrongArity(f'expected {expected} args, got {num_args}')


# TODO: should this be TypeError, like Python?
class WrongArity(Exception):
    pass


# TODO: should this be NameError, like Python?
class UnboundSymbol(Exception):
    def __init__(self, sym):
        msg = f'{sym} at {sym.meta["source"]}' if 'source' in sym.meta else str(sym)
        super().__init__(msg)
