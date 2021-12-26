from dataclasses import dataclass
from typing import Any, List

from src.lexer.token import Token


class Expr:
    pass


@dataclass
class Assign(Expr):
    name: Token
    value: Expr


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Grouping(Expr):
    expression: Expr


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass
class Variable(Expr):
    name: Token


class Stmt:
    pass


@dataclass
class Block(Stmt):
    statements: List[Stmt]


@dataclass
class Expression(Stmt):
    expression: Expr


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt


@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr
