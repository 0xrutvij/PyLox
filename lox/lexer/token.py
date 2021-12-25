from typing import Any

from lox.lexer.token_type import TokenType


class Token:

    def __init__(self, type_: TokenType, lexeme: str, literal: Any, line: int):
        self.type = type_
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
