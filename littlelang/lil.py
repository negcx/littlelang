from typing import Protocol, Callable


class EnvProtocol(Protocol):
    def define(self, name: str, value: any) -> any:
        pass

    def get(self, name: str) -> any:
        pass

    def set(self, name: str, value: any) -> any:
        pass

    def new_scope(self) -> "EnvProtocol":
        pass


class EvalProtocol(Protocol):
    def lil_eval(
        self, env: EnvProtocol, root_eval: Callable[[EnvProtocol, "EvalProtocol"], any]
    ) -> any:
        pass


class LilReaderError(Exception):
    pass


class EOF(LilReaderError):
    pass


class UnexpectedToken(LilReaderError):
    pass


class LilReader:
    def __init__(self, code, debug=False):
        self.code = code
        self.debug = debug
        self.pos = 0
        self.line = 1

    def peek(self, n: int = 1) -> str:
        return self.code[self.pos : (self.pos + n)]

    def consume(self, n: int = 1) -> str:
        chars = self.peek(n)
        self.pos += n
        return chars

    # def try_consume(self, chars) -> bool:
    #     if self.peek[len(chars)] == chars:
    #         self.consume(len(chars))
    #         return True
    #     return False

    # def assert_consume(self, expected):
    #     actual = self.peek[len(expected)]
    #     if actual == expected:
    #         self.consume(len(expected))
    #     else:
    #         raise UnexpectedToken(f"Expected: {expected}, actual {actual}")
