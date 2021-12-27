from __future__ import annotations

from typing import Any

from src.error_handler import LoxRuntimeError
from src.lexer.token import Token


class Environment:

    def __init__(self, encl: Environment = None):
        self.values = dict()
        self.enclosing = encl

    def define(self, name: str, value: Any):
        self.values[name] = value

    def ancestor(self, distance: int) -> Environment:
        env = self
        for _ in range(distance):
            env = env.enclosing

        return env

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).values[name.lexeme] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
