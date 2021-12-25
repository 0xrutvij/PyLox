from abc import ABC
from typing import TypedDict, Dict

import sys
sys.path.append("/Users/rutvijshah/PycharmProjects/pylox")

from src.lexer.token import Token


class Expr(ABC):
    pass


args_dicts = {
    "Binary": {
        "left": "Expr",
        "operator": "Token",
        "right": "Expr"
    },
    "Grouping": {
        "expression": "Expr"
    },
    "Literal": {
        "value": "object"
    },
    "Unary": {
        "operator": "Token",
        "right": "Expr"
    }
}


def gen_init(self, **kwargs):
    self.__dict__.update(kwargs)


def dict_opener(dicti):
    mstrings = []
    for key, val in dicti.items():
        mstrings.append(f"{key}='{val}',")

    return " ".join(mstrings)


def init_creator(cls_name, args_dict):
    estring = f"""def {cls_name}_init(self, {dict_opener(args_dict)}):
        self.__dict__.update({repr(args_dict)})
    """
    return estring


for k, v in args_dicts.items():
    exec(init_creator(k, v))
    locals()[k] = type(k, (Expr,), {"__init__": locals()[f"{k}_init"]})