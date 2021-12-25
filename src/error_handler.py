from src.lexer.token import Token
from src.lexer.token_type import TokenType
had_error = False


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


class ParseError(Exception):
    pass
