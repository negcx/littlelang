from dataclasses import dataclass
from typing import List, Protocol, Tuple


class LilEnvironmentProtocol(Protocol):
    def define(self, name: str, value: any) -> any:
        pass

    def get(self, name: str) -> any:
        pass

    def set(self, name: str, value: any) -> any:
        pass

    def new_scope(self) -> "LilEnvironmentProtocol":
        pass

    def load(self, key_value_pairs: List[Tuple[str, any]]):
        for k, v in key_value_pairs:
            self.define(k, v)


@dataclass
class Position:
    pos: int = 0
    line: int = 0
    line_pos: int = 0


@dataclass
class Node:
    pos: Position


@dataclass
class Literal(Node):
    def val(self):
        return self.value


@dataclass
class Vector(Node):
    children: List[Node]


@dataclass
class Str(Literal):
    value: str


@dataclass
class Float(Literal):
    value: float


@dataclass
class Int(Literal):
    value: int


@dataclass
class Bool(Literal):
    value: bool


@dataclass
class Nil(Literal):
    value = None


@dataclass
class Identifier(Node):
    name: str


@dataclass
class Expression(Node):
    children: List[Node]


@dataclass
class Block(Node):
    children: List[Node]


@dataclass
class Code(Node):
    children: List[Node]
    env: LilEnvironmentProtocol | None = None

    def to_expression(self):
        return Expression(children=self.children, pos=self.pos)


class LilSyntaxError(Exception):
    pass


class LilRuntimeError(Exception):
    pass
