from enum import Enum, auto
from typing import List
from collections import defaultdict

from src.asts.syntax_trees import Block, Stmt, Expr, Var, Variable, Assign, Function, Print, Return, While, Binary, \
    Call, Grouping, Literal, Logical, Unary, Expression, If
from src.common.visitor import visitor
from src.error_handler import resolution_error
from src.lexer.token import Token
from src.parser.interpreter import Interpreter


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()


class Resolver:

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE

    def resolve(self, stmt_expr: Stmt | Expr | List[Stmt]):
        if isinstance(stmt_expr, Stmt) or isinstance(stmt_expr, Expr):
            return self.visit(stmt_expr)
        else:
            for stmt in stmt_expr:
                self.resolve(stmt)

    def resolve_stmts(self, statements: List[Stmt]):
        for statement in statements:
            self.resolve(statement)

    def begin_scope(self):
        self.scopes.append(defaultdict(bool))

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]

        if name.lexeme in scope:
            resolution_error(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token):
        i = len(self.scopes) - 1
        while i >= 0:
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
            i -= 1

    def resolve_function(self, function: Function, type_: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type_
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    @visitor(Block)
    def visit(self, stmt: Block):
        self.begin_scope()
        self.resolve_stmts(stmt.statements)
        self.end_scope()
        return None

    @visitor(Expression)
    def visit(self, stmt: Expression):
        self.resolve(stmt.expression)
        return None

    @visitor(If)
    def visit(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.then_branch is not None:
            self.resolve(stmt.else_branch)
        return None

    @visitor(Var)
    def visit(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
        return None

    @visitor(Variable)
    def visit(self, expr: Variable):
        if self.scopes and not self.scopes[-1][expr.name.lexeme]:
            resolution_error(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)
        return None

    @visitor(Assign)
    def visit(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    @visitor(Function)
    def visit(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    @visitor(Print)
    def visit(self, stmt: Print):
        self.resolve(stmt.expression)
        return None

    @visitor(Return)
    def visit(self, stmt: Return):

        if self.current_function is FunctionType.NONE:
            resolution_error(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            self.resolve(stmt.value)

        return None

    @visitor(While)
    def visit(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    @visitor(Binary)
    def visit(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    @visitor(Call)
    def visit(self, expr: Call):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

        return None

    @visitor(Grouping)
    def visit(self, expr: Grouping):
        self.resolve(expr.expression)
        return None

    @visitor(Literal)
    def visit(self, _: Literal):
        return None

    @visitor(Logical)
    def visit(self, expr: Logical):
        self.resolve(expr.right)
        self.resolve(expr.left)
        return None

    @visitor(Unary)
    def visit(self, expr: Unary):
        self.resolve(expr.right)
        return None

