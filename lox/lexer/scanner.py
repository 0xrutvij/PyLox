from typing import List, Any

from lox.lexer.token import Token
from lox.lexer.token_type import TokenType, keywords
from lox.error_handler import error


class Scanner:
    tokens: List[Token]
    start: int = 0
    current: int = 0
    line: int = 1

    def __init__(self, source: str):
        self.source = source
        self.tokens = []

    def scan_tokens(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _scan_token(self) -> None:
        char: str = self._advance()

        match char:
            case "(":
                self._add_token(TokenType.LEFT_PAREN)

            case ")":
                self._add_token(TokenType.RIGHT_PAREN)

            case "{":
                self._add_token(TokenType.LEFT_BRACE)

            case "}":
                self._add_token(TokenType.RIGHT_BRACE)

            case ",":
                self._add_token(TokenType.COMMA)

            case ".":
                self._add_token(TokenType.DOT)

            case "-":
                self._add_token(TokenType.MINUS)

            case "+":
                self._add_token(TokenType.PLUS)

            case ";":
                self._add_token(TokenType.SEMICOLON)

            case "*":
                self._add_token(TokenType.STAR)

            case "!":
                self._add_token(TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG)

            case "=":
                self._add_token(TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL)

            case "<":
                self._add_token(TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS)

            case ">":
                self._add_token(TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER)

            case "/":
                if self._match("/"):
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                else:
                    self._add_token(TokenType.SLASH)

            case " " | "\r" | "\t":
                pass

            case "\n":
                self.line += 1

            case "\"":
                self._string()

            case char if char.isdecimal():
                self._number()

            case char if char.isidentifier():
                self._identifier()

            case _:
                error(self.line, f"Unexpected character {char}.")

    def _advance(self) -> str:
        next_char = self.source[self.current]
        self.current += 1
        return next_char

    def _add_token(self, type_: TokenType, literal: Any = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type_, text, literal, self.line))

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        elif self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _string(self) -> None:
        while self._peek() != "\"" and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            self._advance()

        if self._is_at_end():
            error(self.line, "Unterminated string.")
            return

        self._advance()

        value = self.source[self.start + 1: self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _number(self) -> None:
        while self._peek().isdecimal():
            self._advance()

        if self._peek() == "." and self._peek_next().isdecimal():
            self._advance()

        while self._peek().isdecimal():
            self._advance()

        self._add_token(
            TokenType.NUMBER,
            float(self.source[self.start: self.current])
        )

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def _identifier(self):
        while self._peek().isalnum():
            self._advance()

        text = self.source[self.start: self.current]
        type_ = keywords.get(text, None) or TokenType.IDENTIFIER
        self._add_token(type_)
