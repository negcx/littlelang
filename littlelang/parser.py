"""
What types of "things" do we have?
* Literals (int, float, boolean, null/nil, string)
* Whitespace (ignored)
* Parenthesis (creates and closes a node)
* Symbols
* Node reference '()



"""

from littlelang.types import (
    Position,
    Str,
    Bool,
    Int,
    Float,
    Block,
    Expression,
    Code,
    LilSyntaxError,
    Identifier,
    Nil,
    Vector,
)

WHITESPACE = ["\n", "\t", " ", "\r"]


class Parser:
    def __init__(self, code, trace=True):
        self.code = code
        self.trace = trace
        self.pos = Position()

    def _node_factory(self, node, **kwargs):
        n = node(pos=self.pos, **kwargs)
        self._trace(n)
        return n

    def _trace(self, message):
        if self.trace:
            print(message)

    def _peek(self):
        return self.code[self.pos.pos : (self.pos.pos + 1)]

    def _consume(self):
        token = self.code[self.pos.pos : (self.pos.pos + 1)]
        if token == "\n":
            self.pos.line += 1
            self.pos.line_pos = 0
        else:
            self.pos.line_pos += 1

        self.pos.pos += 1
        return token

    def _eof(self):
        return self.pos.pos >= len(self.code)

    def _expression(self):
        children = []
        while not self._eof() and self._peek() != ")":
            if t := self._token():
                children.append(t)
        if self._eof() and self._peek() != ")":
            self._syntax_error(
                "There's no more code but I was expecting a closing ')'."
            )
        return self._node_factory(Expression, children=children)

    def _vector(self):
        children = []
        while not self._eof() and self._peek() != "]":
            if t := self._token():
                children.append(t)
        if self._eof() and self._peek() != ")":
            self._syntax_error(
                "There's no more code but I was expecting a closing ']'."
            )
        return self._node_factory(Vector, children=children)

    def _syntax_error(self, message):
        raise LilSyntaxError(
            f"[Syntax Error] Line: {self.pos.line}, "
            "Position: {self.pos.line_pos} - {message}"
        )

    def _number(self):
        n = ""
        decimals = 0
        while self._peek() not in [*WHITESPACE, ")", "]"] and not self._eof():
            ch = self._consume()
            match ch:
                case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                    n += ch
                case ".":
                    decimals += 1
                    n += ch
                case _:
                    self._syntax_error(
                        f"Unexpected character while trying to read a number: {ch}"
                    )
        if decimals > 1:
            self._syntax_error(f"Too many decimal points in the number: {n}")
        elif decimals == 1:
            return self._node_factory(Float, value=float(n))
        else:
            return self._node_factory(Int, value=int(n))

    def _string(self):
        s = ""
        while self._peek() != '"' and not self._eof():
            ch = self._consume()
            if ch != "\\":
                s += ch
            else:
                escape = self._consume()
                match escape:
                    case '"':
                        s += '"'
                    case "\\":
                        s += "\\"
                    case "n":
                        s += "\n"
                    case "t":
                        s += "\t"
                    case "r":
                        s += "\r"
                    case x:
                        s += x
        if self._peek() != '"' and self._eof():
            self._syntax_error("Expected end quote")

        return self._node_factory(Str, value=s)

    def _identifier(self):
        identifier = ""
        while self._peek() not in [*WHITESPACE, ")", "]"] and not self._eof():
            identifier += self._consume()

        match identifier:
            case "nil":
                return self._node_factory(Nil)
            case "true":
                return self._node_factory(Bool, value=True)
            case "false":
                return self._node_factory(Bool, value=False)

        return self._node_factory(Identifier, name=identifier)

    def _token(self):
        match self._peek():
            case " " | "\n" | "\t" | "\r":
                self._consume()
                return None
            case "[":
                self._consume()
                t = self._vector()
                self._consume()
                return t
            case "(":
                self._consume()
                t = self._expression()
                self._consume()
                return t
            case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                return self._number()
            case '"':
                self._consume()
                t = self._string()
                self._consume()
                return t
            case "'":
                self._consume()
                if self._peek() != "(":
                    self._syntax_error("Expected ( after '.")
                self._consume()
                t = self._expression()
                self._consume()
                return Code(pos=t.pos, children=t.children)
            case _:
                return self._identifier()

    def parse(self):
        children = []
        while not self._eof():
            if t := self._token():
                children.append(t)
        return self._node_factory(Block, children=children)
