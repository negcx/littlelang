from littlelang.types import (
    Block,
    Expression,
    Code,
    Identifier,
    Literal,
    LilRuntimeError,
    Node,
    LilEnvironmentProtocol,
    Vector,
)

from typing import Protocol, List


class MissingIdentifier:
    pass


class MissingIdentifierException(Exception):
    pass


class LilEnvironment(LilEnvironmentProtocol):
    def __init__(self, enclosing=None):
        self._enclosing = enclosing
        self._env = {}

    def define(self, name, value):
        if name in self._env:
            raise LilRuntimeError(f"[Runtime Error] {name} is already defined")
        self._env[name] = value
        return value

    def get(self, name):
        if name not in self._env and self._enclosing is None:
            raise LilRuntimeError(f"[Runtime Error] {name} is not defined")
        elif name not in self._env:
            return self._enclosing.get(name)
        return self._env[name]

    def set(self, name, value):
        if name not in self._env and self._enclosing is None:
            raise LilRuntimeError(f"[Runtime Error] {name} is not defined")
        elif name not in self._env:
            return self._enclosing.set(name, value)
        self._env[name] = value
        return value

    def new_scope(self):
        return LilEnvironment(self)

    def load(self, d: dict):
        for k, v in d.items():
            self.define(k, v)


def _runtime_error(node, message):
    raise LilRuntimeError(
        f"[Runtime Error] Line: {node.pos.line}, Position: {node.pos.line_pos}"
        f" - {message}"
        f"{node}"
    )


def function(params_code: Code, body: Code):
    def Function(*args):
        scope = params_code.env.new_scope()
        if len(params_code.children) != len(args):
            raise LilRuntimeError(f"Expected {len(params_code)} args, got {len(args)}")
        if len(params_code.children) != len(
            list(filter(lambda x: isinstance(x, Identifier), params_code.children))
        ):
            raise LilRuntimeError("All params must be identifiers")
        binds = dict(zip(list(map(lambda x: x.name, params_code.children)), args))
        scope.load(binds)

        return run(scope, body.to_expression())

    return Function


PRELUDE = {
    "and": lambda *a: all(a),
    "or": lambda *a: any(a),
    "all": lambda a: all(a),
    "any": lambda a: any(a),
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "abs": lambda a: abs(a),
    "in": lambda a, b: a in b,
    "list": lambda *a: list(a),
    "not": lambda a: not a,
    "map": lambda collection, function: list(map(lambda x: function(x), collection)),
    "filter": lambda collection, function: list(
        filter(lambda x: function(x), collection)
    ),
    "print": lambda p: print(p),
    "id": lambda x: x,
    "len": lambda x: len(x),
    "fn": function,
}


def run(env: LilEnvironmentProtocol, node: Node):
    match node:
        case Literal():
            return node.val()
        case Code():
            node.env = env
            return node
        case Identifier():
            return env.get(node.name)
        case Expression():
            evaluated_children = list(map(lambda c: run(env, c), node.children))

            if len(evaluated_children) < 1:
                _runtime_error(node, "Expressions must have at least one element")

            if not callable(evaluated_children[0]):
                _runtime_error(
                    node,
                    f"The first element of an expression should be a "
                    f"callable function, {evaluated_children[0]}",
                )

            head, *tail = evaluated_children
            return head(*tail)
        case Vector():
            return list(map(lambda c: run(env, c), node.children))

        case Block():
            evaluated_children = list(map(lambda c: run(env, c), node.children))

            if len(evaluated_children) < 1:
                _runtime_error(node, "You must have at least one element")

            return evaluated_children[-1]
