from src.common.visitor import visitor
from src.asts.syntax_trees import Expr, Binary, Grouping, Literal, Unary
from src.lexer.token import Token
from src.lexer.token_type import TokenType


class AstPrinter:

    def print(self, expr: Expr):
        return self.visit(expr)

    @visitor(Binary)
    def visit(self, expr: Binary):
        return paranthesize("", expr.operator.lexeme, expr.left, expr.right)

    @visitor(Grouping)
    def visit(self, expr: Grouping):
        return paranthesize("group", expr.expression)

    @visitor(Literal)
    def visit(self, expr: Literal):
        return repr(expr.value) if expr else "nil"

    @visitor(Unary)
    def visit(self, expr: Unary):
        return paranthesize("", expr.operator.lexeme, expr.right)


def paranthesize(name="", *args):
    subtrees = []
    for arg in args:
        if isinstance(arg, Expr):
            # necessitated since PyTypeChecker doesn't seem
            # to detect derived classes of Expr class.
            # noinspection PyTypeChecker
            subtrees.append(AstPrinter().visit(arg))
        else:
            subtrees.append(arg)

    return f"({name + ' ' if name else name}{' '.join(subtrees)})"


if __name__ == "__main__":
    expression = Binary(
        left=Unary(
            operator=Token(TokenType.MINUS, "-", None, 1),
            right=Literal(value=123)
        ),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=Grouping(expression=Literal(45.67))
    )

    print(AstPrinter().visit(expression))
