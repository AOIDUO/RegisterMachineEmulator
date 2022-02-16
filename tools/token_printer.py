#!/usr/bin/env python3
import argparse

from choco.lexer import TokenKind, Tokenizer
from choco.lexer import Scanner
from choco.lexer import Lexer

parser = argparse.ArgumentParser(description='114514')
parser.add_argument('file', type=argparse.FileType('r'))
args = parser.parse_args()
s = args.file
lxr = Lexer(s)

while True:
	token = lxr.consume()
	print(token.__repr__() + " " + str(token.line+1)+":"+str(token.col+1))
	if lxr.peek().kind == TokenKind.EOF:
		break