from src.lexer.token import Token
from src.lexer.token_type import TokenType

had_error = False
had_runtime_error = False


class LoxRuntimeError(RuntimeError):

    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class ParseError(Exception):
    pass


def error(line: int, message: str):
    report(line, "", message)


def report(line: int, where: str, message: str):
    print(f"[line {line}] Error {where}: {message}")
    global had_error
    had_error = True


def parsing_error(token: Token, message: str):

    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)


def runtime_error(err: LoxRuntimeError):
    msg = " ".join(map(str, err.args))
    print(msg + f"\n[line {err.token.line}]")
    global had_runtime_error
    had_runtime_error = True
