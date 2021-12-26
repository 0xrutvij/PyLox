from typing import Any, List

from src.asts.syntax_trees import (Literal, Grouping, Expr, Unary, Binary,
                                   Expression, Print, Stmt, Var, Variable,
                                   Assign, Block, If, Logical, While, Call, Function, Return)
from src.common.environment import Environment
from src.common.lox_callable import LoxCallable
from src.common.lox_function import LoxFunction
from src.common.return_unwind import ReturnUnwind
from src.common.visitor import visitor
from src.error_handler import LoxRuntimeError, runtime_error
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.parser.native_functions import NativeClock


class Interpreter:

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        self.globals.define("clock", NativeClock())

    def interpret(self, statments: List[Stmt]):
        try:
            for statement in statments:
                self.execute(statement)
        except LoxRuntimeError as err:
            runtime_error(err)

    def execute(self, stmt: Stmt):
        # noinspection PyTypeChecker
        return self.visit(stmt)

    def execute_block(self, statements: List[Stmt], environ: Environment):

        previous: Environment = self.environment
        try:
            self.environment = environ

            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def evaluate(self, expr: Expr):
        # noinspection PyTypeChecker
        return self.visit(expr)

    @visitor(Return)
    def visit(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise ReturnUnwind(value)

    @visitor(Function)
    def visit(self, stmt: Function):
        function: LoxFunction = LoxFunction(stmt)
        self.environment.define(stmt.name.lexeme, function)
        return None

    @visitor(Block)
    def visit(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(encl=self.environment))
        return None

    @visitor(Expression)
    def visit(self, stmt: Expression):
        self.evaluate(stmt.expression)
        return None

    @visitor(If)
    def visit(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

        return None

    @visitor(Print)
    def visit(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    @visitor(Var)
    def visit(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        return None

    @visitor(While)
    def visit(self, stmt: While):

        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

        return None

    @visitor(Assign)
    def visit(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    @visitor(Variable)
    def visit(self, expr: Variable):
        return self.environment.get(expr.name)

    @visitor(Literal)
    def visit(self, expr: Literal):
        return expr.value

    @visitor(Logical)
    def visit(self, expr: Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    @visitor(Grouping)
    def visit(self, expr: Grouping):
        return self.evaluate(expr.expression)

    @visitor(Unary)
    def visit(self, expr: Unary):
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return - float(right)

        return None

    @visitor(Binary)
    def visit(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:

            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)

            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)

            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)

            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)

            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)

            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)

            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if float(right) == 0:
                    raise LoxRuntimeError(expr.operator, "Division by zero is undefined.")
                return float(left) / float(right)

            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)

            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")

        return None

    @visitor(Call)
    def visit(self, expr: Call):
        callee = self.evaluate(expr.callee)

        arguments = []

        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = callee
        if len(arguments) != function.arity():
            raise LoxRuntimeError(expr.paren,
                                  f"Expected {function.arity()} arguments but got {len(arguments)}.")
        return function.call(self, arguments)

    @staticmethod
    def is_truthy(obj: Any) -> bool:
        if obj is None:
            return False
        elif isinstance(obj, bool):
            return obj
        else:
            return True

    @staticmethod
    def is_equal(a, b) -> bool:
        return a == b

    @staticmethod
    def check_number_operand(operator: Token, operand: Any):
        if isinstance(operand, float):
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    @staticmethod
    def check_number_operands(operator: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return

        raise LoxRuntimeError(operator, "Operands must be numbers.")

    @staticmethod
    def stringify(obj):
        if obj is None:
            return "nil"

        elif isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        elif isinstance(obj, bool):
            return "true" if obj else "false"

        else:
            return str(obj)
