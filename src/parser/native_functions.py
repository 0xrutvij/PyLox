import time
from typing import Any, List

from src.common.lox_callable import LoxCallable


class NativeClock(LoxCallable):

    def call(self, interpreter, arguments: List[Any]) -> Any:
        return float(round(time.time()))

    def arity(self) -> int:
        return 0

    def __str__(self):
        return "<native fn>"
