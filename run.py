#!/usr/bin/python3

from typing import NamedTuple
import re

import string


class bcolors:
    """Styleized Text in Terminal

    View all examples by running:
        msg = ""
        x = 0
        for i in range(24):
            for j in range(5):
                code = str(x + j)
                msg += "\33[" + code + "m\\33[" + code + "m\033[0m "
            msg += "\n"
            x += 5

        print(msg)
    """

    # Special
    CEND: str = "\33[0m"
    CBOLD: str = "\33[1m"
    CITALIC: str = "\33[3m"
    CUNDERLINE: str = "\33[4m"
    CBLINK: str = "\33[5m"
    CBLINK2: str = "\33[6m"
    CSELECTED: str = "\33[7m"
    CCROSSEDOUT: str = "\33[9m"

    # Colors 1
    CBLACK: str = "\33[30m"
    CRED: str = "\33[31m"
    CGREEN: str = "\33[32m"
    CYELLOW: str = "\33[33m"
    CBLUE: str = "\33[34m"
    CVIOLET: str = "\33[35m"
    CCYAN: str = "\33[36m"
    CWHITE: str = "\33[37m"

    # Colors 2
    CGREY: str = "\33[90m"
    CRED2: str = "\33[91m"
    CGREEN2: str = "\33[92m"
    CYELLOW2: str = "\33[93m"
    CBLUE2: str = "\33[94m"
    CVIOLET2: str = "\33[95m"
    CCYAN2: str = "\33[96m"
    CWHITE2: str = "\33[97m"

    # Backgrounds 1
    CBLACKBG: str = "\33[40m"
    CREDBG: str = "\33[41m"
    CGREENBG: str = "\33[42m"
    CYELLOWBG: str = "\33[43m"
    CBLUEBG: str = "\33[44m"
    CVIOLETBG: str = "\33[45m"
    CCYANBG: str = "\33[46m"
    CWHITEBG: str = "\33[47m"

    # Backgrounds 2
    CGREYBG: str = "\33[100m"
    CREDBG2: str = "\33[101m"
    CGREENBG2: str = "\33[102m"
    CYELLOWBG2: str = "\33[103m"
    CBLUEBG2: str = "\33[104m"
    CVIOLETBG2: str = "\33[105m"
    CCYANBG2: str = "\33[106m"
    CWHITEBG2: str = "\33[107m"


class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int


"""Produce a Regex Expression that Exactly Matches a String"""
string_as_exp = lambda text: r"".join(map(lambda char: char if char in (string.ascii_letters + string.digits) else f"\\{char}", text))

"""Produce a Regex Expression that Exactly Matches Any Single String from a List of Strings"""
list_as_exp = lambda texts: r"\b(?:" + r"|".join(map(string_as_exp, sorted(texts, key=lambda x: len(x), reverse=True))) + r")\b"


def create_tokens_regex():
    # Built-In Variables
    pine_builtin_variables: list[str] = open("builtin_vars.txt", mode="r", encoding="utf-8").read().split("\n")
    PINE_BUILTIN_VARIABLES_EXP: str = list_as_exp(pine_builtin_variables)

    # Built-in Functions
    pine_builtin_funcs: list[str] = open("builtin_funcs.txt", mode="r", encoding="utf-8").read().split("\n")
    PINE_BUILTIN_FUNCTIONS_EXP: str = list_as_exp(pine_builtin_funcs)

    token_specifications = (
        # User Comments
        ("COMMENT", r"\/\/.+"),
        # Whitespace
        ("INDENT", r"\ {4}|\t"),
        ("NEWLINE", r"\n+"),
        ("SPACE", r" +"),
        # Commas
        ("COMMA", r"\,"),
        # Handling Parenthesis (Might encapsulate both functions and expressions?)
        ("PAREN_OPEN", r"\("),
        ("PAREN_CLOSE", r"\)"),
        # Handling Subscripts
        ("SUBSCRIPT", r"\[\d+\]"),
        # Boolean Logic (Ternary)
        ("IF_TERN", r"\?"),
        ("THEN_TERN", r"\:"),
        # Looping Logic
        ("FOR", r"\bfor\b"),
        ("TO", r"\bto\b"),
        # Boolean Logic
        ("IF", r"\bif\b"),
        ("THEN", r"\bthen\b"),
        ("ELSE", r"\belse\b"),
        ("AND", r"\band\b"),
        ("NOT", r"\bnot\b"),
        ("OR", r"\bor\b"),
        # Comparisons
        ("EQ", r"\=\="),  # Must be placed before remaining
        ("NE", r"\!\="),  # Must be placed before remaining
        ("LE", r"\<\="),  # Must be placed before remaining
        ("GE", r"\>\="),  # Must be placed before remaining
        ("LT", r"\<"),
        ("GT", r"\>"),
        # Applicable to numerical expressions
        ("MODULUS", r"\%"),
        ("MULTIPLY", r"\*"),
        ("ADD", r"\+"),
        ("SUBTRACT", r"\-"),
        ("DIVIDE", r"\/"),
        # Assignment
        ("DECLARE", r"\="),
        ("ASSIGN", r"\:\="),
        # Built-In
        #     Variables
        ("VAR_BUILTIN", PINE_BUILTIN_VARIABLES_EXP),  # Must be placed before remaining
        #     Functions
        ("FUNC_BUILTIN", PINE_BUILTIN_FUNCTIONS_EXP),  # Must be placed before remaining
        # User
        #     Function Definition
        ("FUNC_DEF_USER", r"[A-Za-z\_]+\(.+\)\ *\=\>"),
        #     Variable or Function
        ("FUNC_OR_VAR_USER", r"[A-Za-z\_]+[A-Za-z\_0-9]*"),
        ("NUMBER", r"\d+(\.\d*)?"),
        ("CONTINUE", r"\bcontinue\b"),
        ("BREAK", r"\bbreak\b"),
    )
    tokens_regex = re.compile(r"|".join("(?P<%s>%s)" % pair for pair in token_specifications))
    return tokens_regex


def tokenize(code):
    tokens_regex = create_tokens_regex()
    print("tokens_regex:".rjust(38) + '"' + tokens_regex.pattern + '"')

    # TODO: Track Known Functions and Variables
    # known_funcs = []
    # known_vars = []

    test_code = ""

    line_num = 1
    line_start = 0
    for found in tokens_regex.finditer(code):
        kind = found.lastgroup
        # print(f"Kind: {kind}")
        value = found.group()
        # print(f"Value: {value}")
        column = found.start() - line_start
        # print(f"Column: {column}")

        # User Comments
        if kind == "COMMENT":
            # Clean Comment Text
            value = value.lstrip(" /").rstrip(" ")
        # Whitespace
        elif kind == "INDENT":
            test_code += bcolors.CGREYBG + "<indent>" + bcolors.CEND

            # Stay Silent for Now
            continue
        elif kind == "NEWLINE":
            test_code += "\n"

            # Increment for Tracking Rows
            line_start = found.end()
            line_num += 1
            continue
        elif kind == "SPACE":
            # Stay Silent for Now
            continue
        # Commas
        elif kind == "COMMA":
            test_code += bcolors.CYELLOW + ", " + bcolors.CEND
        # Handling Parenthesis (Might encapsulate both functions and expressions?)
        elif kind == "PAREN_OPEN":
            test_code += "("
        elif kind == "PAREN_CLOSE":
            test_code += ")"
        # Handling Subscripts
        elif kind == "SUBSCRIPT":
            # Remove Surrounding Braces
            value = value.strip(" []")

            test_code += bcolors.CBLUE + "{" + kind + " of " + value + "}" + bcolors.CEND
        # Boolean Logic (Ternary)
        elif kind == "IF_TERN":
            test_code += " if "
        elif kind == "ELSE_TERN":
            test_code += " else "
        # Looping Logic
        elif kind == "FOR":
            test_code += bcolors.CBLUE + "{" + kind + "}" + bcolors.CEND
        elif kind == "TO":
            test_code += bcolors.CBLUE + " {" + kind + "} " + bcolors.CEND
        # Boolean Logic
        elif kind == "IF":
            test_code += bcolors.CBLUE + "if " + bcolors.CEND
        elif kind == "THEN":
            test_code += bcolors.CBLUE + "{" + kind + "}" + bcolors.CEND
        elif kind == "ELSE":
            test_code += bcolors.CBLUE + "else:" + bcolors.CEND
        elif kind == "AND":
            test_code += bcolors.CBLUE + " and " + bcolors.CEND
        elif kind == "NOT":
            test_code += bcolors.CBLUE + " not " + bcolors.CEND
        elif kind == "OR":
            test_code += bcolors.CBLUE + "{" + kind + "}" + bcolors.CEND
        # Comparisons
        elif kind == "EQ":
            test_code += bcolors.CCYAN + " == " + bcolors.CEND
        elif kind == "NE":
            test_code += bcolors.CCYAN + " != " + bcolors.CEND
        elif kind == "LE":
            test_code += bcolors.CCYAN + " <= " + bcolors.CEND
        elif kind == "GE":
            test_code += bcolors.CCYAN + " >= " + bcolors.CEND
        elif kind == "LT":
            test_code += bcolors.CCYAN + " < " + bcolors.CEND
        elif kind == "GT":
            test_code += bcolors.CCYAN + " > " + bcolors.CEND
        # Applicable to numerical expressions
        elif kind == "MODULUS":
            test_code += bcolors.CYELLOW + " % " + bcolors.CEND
        elif kind == "MULTIPLY":
            test_code += bcolors.CYELLOW + " * " + bcolors.CEND
        elif kind == "ADD":
            test_code += bcolors.CYELLOW + " + " + bcolors.CEND
        elif kind == "SUBTRACT":
            test_code += bcolors.CYELLOW + " - " + bcolors.CEND
        elif kind == "DIVIDE":
            test_code += bcolors.CYELLOW + " / " + bcolors.CEND
        # Assignment
        elif kind == "DECLARE":
            test_code += bcolors.CYELLOW + " = " + bcolors.CEND
        elif kind == "ASSIGN":
            test_code += bcolors.CYELLOW + " = " + bcolors.CEND
        # Built-In Functions
        elif kind == "FUNC_BUILTIN":
            test_code += bcolors.CVIOLET + kind + bcolors.CEND
        # Built-In Varables
        elif kind == "VAR_BUILTIN":
            test_code += bcolors.CCYAN + kind + bcolors.CEND
        # User Function Definition
        elif kind == "FUNC_DEF_USER":
            # TODO: Register as Known User Function
            # known_funcs.append(...
            value = value.strip(" ").removesuffix("=>").rstrip(" ")
            identifier = ""
            for char in value:
                if char != "(":
                    identifier += char
                else:
                    break

            if identifier:
                # Remove Identifier from Text
                value = value.removeprefix(identifier)

            params = []
            # Expects it to be Surrounded in Parenthesis
            if value.startswith("(") and value.endswith(")"):
                # Remove the parenthesis
                value = value.removeprefix("(").removesuffix(")")
                # Collapse Spaces
                value = re.sub(r"\ +", "", value)
                # Parse the Parameters
                params.extend(value.split(","))

            if params:
                # Set Value to the Parameter Names
                value = ",".join(params)

            test_code += bcolors.CBLUEBG + "{" + kind + " with params (" + value + ")}" + bcolors.CEND
        # User-Defined Function or Variable Reference
        elif kind == "FUNC_OR_VAR_USER":
            test_code += bcolors.CBLUEBG + "{" + kind + "}" + bcolors.CEND
        elif kind == "NUMBER":
            # value = float(value) if "." in value else int(value)
            test_code += bcolors.CGREEN + value + bcolors.CEND
        elif kind == "CONTINUE":
            # Same as Python
            test_code += "continue"
        elif kind == "BREAK":
            # Same as Python
            test_code += "break"
        # elif kind == 'SKIP':
        #     continue
        # elif kind == 'MISMATCH':
        #     raise RuntimeError(f'{value!r} unexpected on line {line_num}')

        yield Token(kind, value, line_num, column)

    print(test_code)


def main() -> None:
    print(bcolors.CBOLD + "This script is just a mild proof of concept and is not finished" + bcolors.CEND)
    print()

    # Example script used: https://github.com/samgozman/AO-MACD-cross-tradingview/blob/master/ao-macd-cross-script.pine
    pine_script = open("ao-macd-cross-script.pine", mode="r", encoding="utf-8").read()
    print(bcolors.CBOLD + "We will use the following pine script as an example:" + bcolors.CEND)
    print(bcolors.CGREYBG + pine_script.replace("\n", "    \n") + bcolors.CEND)
    print()

    for token in tokenize(pine_script):
        print(token)


if __name__ == "__main__":
    main()
