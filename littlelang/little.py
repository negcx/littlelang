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

from dataclasses import dataclass
from typing import Any, Callable, List, Union


@dataclass
class Position:
    pos: int = 0
    line: int = 0
    line_pos: int = 0

    def inc(self, ch: str):
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.line_pos = 0


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
        self._env[name] = value

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
    start_pos: Position
    end_pos: Position


@dataclass
class Literal(Node):
    value: LiteralType


class Symbol(Literal):
    """A convenience syntax to separate keys from strings in code.
    In the end, though, it's just a string.

    Example: (fn [:a :b] '(+ a b))
    instead of:
    (fn ["a" "b"] '(+a b))"""

    pass


@dataclass
class Identifier(Node):
    """Bound variable names from the Environment within Little."""

    name: str


@dataclass
class ParentNode(Node):
    children: List[Node]


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


@dataclass
class Quoted(Node):
    """Quoted code is passed as is without evaluation.
    It can later be evaluated within bound functions."""

    node: Node


@dataclass
class QuotedRuntime(Node):
    node: Node
    env: Environment
    exec: Callable[[Environment, Node], Any]


class LittleSyntaxError(Exception):
    def __init__(
        self,
        msg=None,
        start_pos: Position | None = None,
        end_pos: Position | None = None,
    ):
        super().__init__(msg)
        self.start_pos = start_pos
        self.end_pos = end_pos


class UnexpectedToken(LittleSyntaxError):
    pass


class ExpectedToken(LittleSyntaxError):
    pass


class InvalidNumber(LittleSyntaxError):
    pass


class UnexpectedEOF(LittleSyntaxError):
    pass


class MissingMapValue(LittleSyntaxError):
    pass


class Parser:
    WHITESPACE = [" ", "\t", "\r", "\n", "\t", ","]
    END_OF_TOKEN = [*WHITESPACE, "[", "]", "{", "}", "(", ")"]
    IDENTIFIER_CHARACTERS = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "_-/*+-!?$:><=;"
        "0123456789"
    )

    def __init__(self, code):
        self.code = code
        self.pos = Position()

    def _peek(self) -> str:
        return self.code[self.pos.pos : (self.pos.pos + 1)]

    def _consume(self) -> str:
        if self.pos.pos + 1 > len(self.code):
            raise UnexpectedEOF(start_pos=self.pos, end_pos=self.pos)
        ch = self.code[self.pos.pos : (self.pos.pos + 1)]
        self.pos.inc(ch)
        return ch

    def _expect_consume(self, expected_ch) -> str:
        ch = self._consume()
        if ch != expected_ch:
            raise ExpectedToken(expected_ch, start_pos=self.pos, end_pos=self.pos)
        return ch

    def _eof(self) -> bool:
        return self.pos.pos >= len(self.code)

    def _number(self) -> Literal:
        start_pos = self.pos
        number_chars = ""
        decimal_count = 0

        while self._peek() not in Parser.END_OF_TOKEN and not self._eof():
            ch = self._consume()
            match ch:
                case _ if ch.isdigit():
                    number_chars += ch
                case ".":
                    number_chars += ch
                    decimal_count += 1
                case "_":
                    continue
                case _:
                    raise UnexpectedToken(ch, start_pos=self.pos)

        match decimal_count:
            case 0:
                return Literal(
                    value=int(number_chars), start_pos=start_pos, end_pos=self.pos
                )
            case 1:
                return Literal(
                    value=float(number_chars), start_pos=start_pos, end_pos=self.pos
                )
            case _:
                raise InvalidNumber(number_chars, start_pos, self.pos)

    def _string(self) -> Literal:
        start_pos = self.pos
        self._expect_consume('"')
        s = ""
        while self._peek() != '"' and not self._eof():
            ch = self._consume()
            if ch != "\\":
                s += ch
            else:
                escape = self._consume()
                match escape:
                    case "n":
                        s += "\n"
                    case "t":
                        s += "\t"
                    case "r":
                        s += "\r"
                    case _:
                        s += escape

        self._expect_consume('"')

        return Literal(value=s, start_pos=start_pos, end_pos=self.pos)

    def _identifier_string(self) -> str:
        identifier = ""
        while self._peek() not in Parser.END_OF_TOKEN and not self._eof():
            ch = self._consume()
            if ch not in self.IDENTIFIER_CHARACTERS:
                raise UnexpectedToken(ch, start_pos=self.pos, end_pos=self.pos)
            identifier += ch
        return identifier

    def _identifier(self) -> Identifier | Literal:
        start_pos = self.pos
        return Identifier(
            name=self._identifier_string(), start_pos=start_pos, end_pos=self.pos
        )

    def _symbol(self) -> Literal:
        start_pos = self.pos
        self._expect_consume(":")
        symbol = self._identifier_string()
        return Symbol(value=symbol, start_pos=start_pos, end_pos=self.pos)

    def _children(self, start_char, end_char) -> list[Node]:
        children = []
        self._expect_consume(start_char)
        while not self._eof() and self._peek() != end_char:
            if node := self._node():
                children.append(node)
        if self._eof() and self._peek() != end_char:
            raise ExpectedToken(end_char, start_pos=self.pos, end_pos=self.pos)
        self._expect_consume(end_char)

        return children

    def _quoted(self) -> Quoted:
        start_pos = self.pos
        self._expect_consume("'")
        node = self._node()
        if node is None:
            raise ExpectedToken(start_pos=start_pos, end_pos=self.pos)
        return Quoted(node=node, start_pos=start_pos, end_pos=self.pos)

    def _vector(self) -> Vector:
        start_pos = self.pos
        children = self._children("[", "]")
        return Vector(children=children, start_pos=start_pos, end_pos=self.pos)

    def _map(self) -> Map:
        start_pos = self.pos
        children = self._children("{", "}")

        if len(children) % 2 != 0:
            raise MissingMapValue(start_pos=start_pos, end_pos=self.pos)

        return Map(children=children, start_pos=start_pos, end_pos=self.pos)

    def _expression(self) -> Expression:
        start_pos = self.pos
        children = self._children("(", ")")
        return Expression(children=children, start_pos=start_pos, end_pos=self.pos)

    def _node(self) -> Node | None:
        ch = self._peek()
        match ch:
            case _ if ch in Parser.WHITESPACE:
                self._consume()
            case _ if ch.isdigit():
                return self._number()
            case '"':
                return self._string()
            case ":":
                return self._symbol()
            case "[":
                return self._vector()
            case "{":
                return self._map()
            case "(":
                return self._expression()
            case _ if ch in Parser.IDENTIFIER_CHARACTERS:
                return self._identifier()
            case "'":
                return self._quoted()
            case _:
                raise UnexpectedToken(ch, start_pos=self.pos, end_pos=self.pos)

        return None

    def parse(self) -> list[Node]:
        nodes = []
        while not self._eof():
            if node := self._node():
                nodes.append(node)
        return nodes


def _exec(env: Environment, node: Node) -> Any:
    match node:
        case Literal():
            return node.value
        case Vector():
            return list(map(lambda child: _exec(env, child), node.children))
        case Map():
            values = list(map(lambda child: _exec(env, child), node.children))
            return dict(
                map(
                    lambda i: (values[i], values[i + 1]),
                    range(0, len(values), 2),
                )
            )
        case Expression():
            values = list(map(lambda child: _exec(env, child), node.children))

            if len(values) == 0:
                raise LittleRuntimeError("Expressions must have at least one element")
            if not callable(values[0]):
                raise LittleRuntimeError(
                    "The first element of an expression must be a function"
                )
            head, *tail = values
            return head(*tail)
        case Identifier():
            return env.get(node.name)
        case Quoted():
            return QuotedRuntime(
                node=node.node,
                env=env,
                exec=_exec,
                start_pos=node.start_pos,
                end_pos=node.end_pos,
            )
        case _:
            return LittleRuntimeError("Not yet implemented!")


class Little:
    def __init__(self):
        self.env = Environment()
        self.env.define("None", None)
        self.env.define("True", True)
        self.env.define("False", False)

    def exec(self, code: str):
        parser = Parser(code)
        return list(map(lambda node: _exec(self.env, node), parser.parse()))[-1]
