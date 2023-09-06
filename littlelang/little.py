"""
What types of "things" do we have?
* Literals (int, float, boolean, None, string)
* Lists (vectors)
* Dictionaries
* Whitespace (ignored)
* Parenthesis (creates and closes a node)
* Symbols
* Node reference '()
"""

from typing import Union
from dataclasses import dataclass


@dataclass
class Position:
    pos: int
    line: int
    line_pos: int


class LittleRuntimeError(Exception):
    pass


class IdentifierNotDefined(LittleRuntimeError):
    pass


class IdentifierAlreadyExists(LittleRuntimeError):
    pass


class Environment:
    """Environments are where state is stored for running Little programs.
    This includes all functions and operators."""

    def __init__(self, parent=None):
        self._parent = parent
        self._env = {}

    def define(self, name, value):
        """Define a new identifier in this scope."""
        if name in self._env:
            raise IdentifierAlreadyExists(name)
        self._env = value

    def get(self, name):
        if name not in self._env:
            if self._parent is None:
                raise IdentifierNotDefined(name)
            return self._parent.get(name)
        return self._env[name]

    def set(self, name, value):
        if name not in self._env:
            if self._parent is None:
                raise IdentifierNotDefined(name)
            return self._parent.set(name, value)
        self._env[name] = value

    def new_scope(self):
        """Create a new lexical scope."""
        return Environment(self)


LiteralType = Union[str, int, bool, float, None]


@dataclass
class Node:
    start: Position
    end: Position


class Literal(Node):
    value: LiteralType


class Symbol(Literal):
    """A convenience syntax to separate keys from strings in code.
    In the end, though, it's just a string.

    Example: (fn [:a :b] '(+ a b))
    instead of:
    (fn ["a" "b"] '(+a b))"""

    pass


class Identifier(Node):
    """Bound variable names from the Environment within Little."""

    name: str


class ParentNode(Node):
    children: list[Node]


class Expression(ParentNode):
    """The fundamental building block for Little programs. Each expression starts with a
    function followed by its arguments."""

    pass


class Vector(ParentNode):
    """Represents a Python List within Little."""

    pass


class Map(ParentNode):
    """Represents a Python Dict within Little."""

    pass


class Quoted(Node):
    """Quoted code is passed as is without evaluation.
    It can later be evaluated within bound functions."""

    node: Node


class Little:
    def exec(self, code: str):
        pass
