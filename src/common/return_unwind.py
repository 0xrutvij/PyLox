from typing import Any


class ReturnUnwind(RuntimeError):
    
    def __init__(self, value: Any):
        super(ReturnUnwind, self).__init__()
        self.value = value
        