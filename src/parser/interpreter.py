from typing import Any, List

from src.asts.syntax_trees import Literal, Grouping, Expr, Unary, Binary, Expression, Print, Stmt
from src.common.visitor import visitor
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.error_handler import LoxRuntimeError, runtime_error


class Interpreter:

    def interpret(self, statments: List[Stmt]):
        try:
            for statement in statments:
                self.execute(statement)
        except LoxRuntimeError as err:
            runtime_error(err)

    def execute(self, stmt: Stmt):
        return self.visit(stmt)

    def evaluate(self, expr: Expr):
        return self.visit(expr)

    @visitor(Expression)
    def visit(self, stmt: Expression):
        self.evaluate(stmt.expression)
        return None

    @visitor(Print)
    def visit(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    @visitor(Literal)
    def visit(self, expr: Literal):
        return expr.value

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
