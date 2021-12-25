from dataclasses import dataclass, field
from typing import Any, Dict

from src.error_handler import LoxRuntimeError
from src.lexer.token import Token


@dataclass
class Environment:
    values: Dict[str, Any] = field(default_factory=dict)

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
