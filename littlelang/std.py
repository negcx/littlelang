from typing import Any, Dict, List

from littlelang.little import Environment, Little, LittleRuntimeError, QuotedRuntime


def function(params: List[str], body: QuotedRuntime):
    def Function(*args):
        scope = body.env.new_scope()
        if len(params) != len(args):
            raise LittleRuntimeError(f"Expected {len(params)} args, got {len(args)}")
        for key, value in zip(params, args, strict=True):
            scope.define(key, value)
        return body.exec(scope, body.node)

    return Function


LOGIC = {
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
    "not": lambda a: not a,
    "in": lambda a, b: a in b,
}

MATH = {"abs": lambda a: abs(a)}

FUNCTION = {
    "fn": function,
}


def get_in(collection: dict, key: List) -> Any:
    head, *tail = key
    if head in collection:
        if len(tail) > 0:
            return get_in(collection[head], tail)
        else:
            return collection[head]
    return None


COLLECTIONS = {
    "map": lambda collection, function: list(map(lambda x: function(x), collection)),
    "filter": lambda collection, function: list(
        filter(lambda x: function(x), collection)
    ),
    "len": lambda x: len(x),
    "get": lambda collection, key: collection[key],
    "get-in": get_in,
}


def print_debug(a):
    print(a)
    return a


CONSOLE_OUTPUT = {"print": lambda p: print(p), "dbg": print_debug}

DO = {"do": lambda *a: a[-1]}


def little_def(name: str, value: QuotedRuntime):
    value.env.define(name, value.exec(value.env, value.node))


DEF = {"def": little_def}


def std(env: Environment):
    STANDARD: List[Dict[str, Any]] = [
        LOGIC,
        MATH,
        FUNCTION,
        COLLECTIONS,
        CONSOLE_OUTPUT,
        DO,
        DEF,
    ]
    for m in STANDARD:
        for key, value in m.items():
            env.define(key, value)


class LittleWithStd(Little):
    def __init__(self, *args):
        super().__init__(*args)
        std(self.env)
