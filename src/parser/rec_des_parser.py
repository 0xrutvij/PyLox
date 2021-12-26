from typing import List, Set

from src.asts.syntax_trees import (Expr, Binary, Unary, Literal, Grouping,
                                   Stmt, Print, Expression, Var, Variable,
                                   Assign, Block, If, Logical, While, Call, Function, Return)
from src.error_handler import parsing_error, ParseError
from src.lexer.token import Token
from src.lexer.token_type import TokenType as Tt


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:

        statements: List[Stmt] = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self) -> Stmt | None:
        try:
            if self.match({Tt.VAR}):
                return self.var_declaration()
            if self.match({Tt.FUN}):
                return self.function("function")
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def var_declaration(self):
        name: Token = self.consume(Tt.IDENTIFIER, "Expect variable name.")

        initializer: Expr | None = None

        if self.match({Tt.EQUAL}):
            initializer = self.expression()

        self.consume(Tt.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self) -> Stmt:
        if self.match({Tt.PRINT}):
            return self.print_statement()
        elif self.match({Tt.LEFT_BRACE}):
            return Block(self.block())
        elif self.match({Tt.IF}):
            return self.if_statement()
        elif self.match({Tt.WHILE}):
            return self.while_statement()
        elif self.match({Tt.FOR}):
            return self.for_statement()
        elif self.match({Tt.RETURN}):
            return self.return_statement()

        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(Tt.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match({Tt.SEMICOLON}):
            initializer = None
        elif self.match({Tt.VAR}):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition: Expr | None = None
        if self.check() != Tt.SEMICOLON:
            condition = self.expression()

        self.consume(Tt.SEMICOLON, "Expect ';' after loop condition.")

        increment: Expr | None = None
        if self.check() != Tt.RIGHT_PAREN:
            increment = self.expression()

        self.consume(Tt.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            # TODO: Maybe change this to False, infinite
            #  loop without a "break" statement implemented is risky
            condition = Literal(True)

        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def while_statement(self) -> Stmt:
        self.consume(Tt.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(Tt.RIGHT_PAREN, "Expect ')' after condition.")
        body: Stmt = self.statement()

        return While(condition, body)

    def if_statement(self) -> Stmt:
        self.consume(Tt.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(Tt.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self.statement()
        else_branch: Stmt | None = None
        if self.match({Tt.ELSE}):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(Tt.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def return_statement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Expr | None = None
        if self.check() != Tt.SEMICOLON:
            value = self.expression()

        self.consume(Tt.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(Tt.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)

    def function(self, kind: str) -> Function:
        name: Token = self.consume(Tt.IDENTIFIER, f"Expect {kind} name.")
        self.consume(Tt.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: List[Token] = []

        if self.check() != Tt.RIGHT_PAREN:
            parameters.append(self.consume(Tt.IDENTIFIER, "Expect parameter name."))
            while self.match({Tt.COMMA}):
                if len(parameters) >= 255:
                    "Can't have more than 255 parameters."
                parameters.append(self.consume(Tt.IDENTIFIER, "Expect parameter name."))

        self.consume(Tt.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(Tt.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: List[Stmt] = self.block()
        return Function(name, parameters, body)

    def block(self):
        statements: List[Stmt] = []

        curr_tok = self.check()
        while (not curr_tok == Tt.RIGHT_BRACE) and (not self.is_at_end()):
            statements.append(self.declaration())
            curr_tok = self.check()

        self.consume(Tt.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr: Expr = self._or()

        if self.match({Tt.EQUAL}):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr: Expr = self._and()

        while self.match({Tt.OR}):
            operator: Token = self.previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr: Expr = self.equality()

        while self.match({Tt.AND}):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)

        return expr

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

        return self.call()

    def call(self) -> Expr:
        expr: Expr = self.primary()

        while True:
            if self.match({Tt.LEFT_PAREN}):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments: List[Expr] = []

        if self.check() != Tt.RIGHT_PAREN:
            arguments.append(self.expression())
            while self.match({Tt.COMMA}):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren: Token = self.consume(Tt.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

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

            case Tt.IDENTIFIER:
                self.advance()
                return Variable(self.previous())

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

            if self.peek().type in {Tt.CLASS, Tt.FUN, Tt.VAR, Tt.FOR,
                                    Tt.IF, Tt.WHILE, Tt.PRINT, Tt.RETURN}:
                return

        self.advance()
