#!/usr/bin/env python3

import argparse
import os
import sys
from io import StringIO
import argparse

from lexer import Lexer as Lexer
from parser import Parser as Parser

from typing import Callable, List


class RegMachineMain:
    args: argparse.Namespace

    def __init__(self, args: argparse.Namespace):
        self.args = args

    def parse(self):
        """Parse the input file."""
        if self.args.input_file is None:
            f = sys.stdin
        else:
            f = open(self.args.input_file, mode='r')

        lexer = Lexer(f)
        parser = Parser(lexer)
        program = parser.parse_input()
        return program

    def emulate(self):
        pass

arg_parser = argparse.ArgumentParser(
    description='1')
arg_parser.add_argument("input_file",
                        type=str,
                        nargs="?",
                        help="Path to input file")


def __main__(args: argparse.Namespace):
    regm_main = RegMachineMain(args)
    print(regm_main.parse())


if __name__ == "__main__":
    args = arg_parser.parse_args()
    __main__(args)
