from typing import Any, List

from src.common.lox_callable import LoxCallable
from src.asts.syntax_trees import Function
from src.common.environment import Environment
from src.common.return_unwind import ReturnUnwind


class LoxFunction(LoxCallable):

    def __init__(self, declaration: Function):
        self.declaration = declaration

    def call(self, interpreter, arguments: List[Any]) -> Any:
        env: Environment = Environment(interpreter.globals)

        for i, param in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnUnwind as runw:
            return runw.value
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
