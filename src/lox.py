from pathlib import Path
from sys import argv, exit

from src import error_handler
from src.lexer.scanner import Scanner
from src.parser.interpreter import Interpreter
from src.parser.rec_des_parser import Parser
from src.parser.resolver import Resolver

PATHLIKE = Path | str
DEBUG_MODE = False


def main(args):
    interpreter = Interpreter()
    if len(args) > 2:
        print("Usage: pylox [script]")
        exit(64)
    elif len(args) == 2:
        run_file(args[1], interpreter)
        if error_handler.had_error:
            exit(65)
        if error_handler.had_runtime_error:
            exit(70)
    else:
        run_prompt(interpreter)


def run_file(script_path: PATHLIKE, interp: Interpreter):

    try:
        with open(script_path, "r") as infile:
            script = infile.read()
            run(script, interp)
    except FileNotFoundError:
        print(f"error: File at {script_path} wasn't found.")


def run_prompt(interp: Interpreter):

    while True:
        try:
            line = input("> ")
            run(line, interp)
            error_handler.had_error = False
        except EOFError:
            print("\nThe only way to learn a new programming language is by writing programs in it. - K&R")
            break


def run(source: str, interp: Interpreter):
    tokens = Scanner(source).scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    if error_handler.had_error:
        return

    resolver = Resolver(interp)
    resolver.resolve(statements)

    # handle resolution errors
    if error_handler.had_error:
        return

    interp.interpret(statements)


if __name__ == "__main__":
    main(argv)
