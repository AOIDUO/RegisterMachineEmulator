#!/usr/bin/env python3

import argparse
import os
import sys
from io import StringIO
import argparse

from choco.lexer import Lexer as ChocoLexer
from choco.parser import Parser as ChocoParser

from typing import Callable, List


class ChocoOptMain:
    args: argparse.Namespace

    def __init__(self, args: argparse.Namespace):
        self.args = args

    def parse(self):
        """Parse the input file."""
        if self.args.input_file is None:
            f = sys.stdin
        else:
            f = open(self.args.input_file, mode='r')

        lexer = ChocoLexer(f)
        parser = ChocoParser(lexer)
        program = parser.parse_input()
        return program


arg_parser = argparse.ArgumentParser(
    description='1')
arg_parser.add_argument("input_file",
                        type=str,
                        nargs="?",
                        help="Path to input file")


def __main__(args: argparse.Namespace):
    choco_main = ChocoOptMain(args)
    print(choco_main.parse())


if __name__ == "__main__":
    args = arg_parser.parse_args()
    __main__(args)
