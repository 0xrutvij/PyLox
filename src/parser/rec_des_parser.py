from typing import List, Set

from src.asts.syntax_trees import Expr, Binary, Unary, Literal, Grouping, Stmt, Print, Expression
from src.lexer.token import Token
from src.lexer.token_type import TokenType as Tt
from src.error_handler import parsing_error, ParseError


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:

        statements: List[Stmt] = []

        while not self.is_at_end():
            statements.append(self.statement())

        return statements

    def statement(self) -> Stmt:
        if self.match({Tt.PRINT}):
            return self.print_statement()

        return self.expression_statement()

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(Tt.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(Tt.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr: Expr = self.comparison()

        while self.match({Tt.BANG_EQUAL, Tt.EQUAL_EQUAL}):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self.match({Tt.GREATER, Tt.GREATER_EQUAL, Tt.LESS, Tt.LESS_EQUAL}):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self.match({Tt.MINUS, Tt.PLUS}):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self.match({Tt.STAR, Tt.SLASH}):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:

        if self.match({Tt.BANG, Tt.MINUS}):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:

        next_token_type = self.check()

        match next_token_type:

            case Tt.FALSE:
                self.advance()
                return Literal(False)

            case Tt.TRUE:
                self.advance()
                return Literal(True)

            case Tt.NIL:
                self.advance()
                return Literal(None)

            case Tt.NUMBER | Tt.STRING:
                self.advance()
                return Literal(self.previous().literal)

            case Tt.LEFT_PAREN:
                self.advance()
                expr: Expr = self.expression()
                self.consume(Tt.RIGHT_PAREN, "Expect ')' after expression.")
                return Grouping(expr)

            case _:
                raise self.error(self.peek(), "Expect expression.")

    def consume(self, type_: Tt, message: str):
        if self.check() == type_:
            return self.advance()

        raise self.error(self.peek(), message)

    def match(self, args: Set[Tt]) -> bool:

        if self.check() in args:
            self.advance()
            return True

        return False

    def check(self) -> Tt | None:
        if self.is_at_end():
            return None
        else:
            return self.peek().type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == Tt.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    @staticmethod
    def error(token: Token, message: str) -> ParseError:
        parsing_error(token, message)
        return ParseError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == Tt.SEMICOLON:
                return

            if self.peek().type in {Tt.CLASS, Tt. FUN, Tt.VAR, Tt.FOR,
                                    Tt.IF, Tt.WHILE, Tt.PRINT. Tt.RETURN}:
                return

        self.advance()
