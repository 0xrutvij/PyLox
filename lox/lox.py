from sys import argv, exit
from pathlib import Path
from lox.lexer.scanner import Scanner
from lox import error_handler

PATHLIKE = Path | str


def main(args):
    if len(args) > 2:
        print("Usage: pylox [script]")
        exit(64)
    elif len(args) == 2:
        run_file(args[1])
        if error_handler.had_error:
            exit(65)
    else:
        run_prompt()


def run_file(script_path: PATHLIKE):

    try:
        with open(script_path, "r") as infile:
            script = infile.read()
            run(script)
    except FileNotFoundError:
        print(f"error: File at {script_path} wasn't found.")


def run_prompt():

    while True:
        try:
            line = input("> ")
            if line == "quit;":
                print("\nThe only way to learn a new programming language is by writing programs in it. - K&R")
                break
            run(line)
            error_handler.had_error = False
        except EOFError:
            print("\nThe only way to learn a new programming language is by writing programs in it. - K&R")
            break


def run(source: str):
    tokens = Scanner(source).scan_tokens()
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main(argv)
