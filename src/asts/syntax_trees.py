from dataclasses import dataclass
from typing import Any, List
from uuid import uuid4

from src.lexer.token import Token


class Expr:
    pass


@dataclass(unsafe_hash=True)
class Assign(Expr):
    name: Token
    value: Expr


@dataclass(unsafe_hash=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(unsafe_hash=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: List[Expr]


@dataclass(unsafe_hash=True)
class Grouping(Expr):
    expression: Expr


@dataclass(unsafe_hash=True)
class Literal(Expr):
    value: Any


@dataclass(unsafe_hash=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(unsafe_hash=True)
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass(unsafe_hash=True)
class Variable(Expr):
    name: Token


class Stmt:
    pass


@dataclass(unsafe_hash=True)
class Block(Stmt):
    statements: List[Stmt]


@dataclass(unsafe_hash=True)
class Expression(Stmt):
    expression: Expr


@dataclass(unsafe_hash=True)
class Function(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]


@dataclass(unsafe_hash=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt


@dataclass(unsafe_hash=True)
class Print(Stmt):
    expression: Expr


@dataclass(unsafe_hash=True)
class Return(Stmt):
    keyword: Token
    value: Expr


@dataclass(unsafe_hash=True)
class Var(Stmt):
    name: Token
    initializer: Expr


@dataclass(unsafe_hash=True)
class While(Stmt):
    condition: Expr
    body: Stmt
