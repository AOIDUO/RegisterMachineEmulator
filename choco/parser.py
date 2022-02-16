from operator import truediv
from xdsl.dialects.builtin import ModuleOp

from choco.lexer import Token, TokenKind, Lexer
import choco.dialects.choco_ast as ast

from typing import List, Optional, Union, Tuple, Dict

from choco.errmsg import *

from choco.instr import *

class Parser:

    def __init__(self, lexer: Lexer):
        """``
        Create a new parser.

        Initialize parser with the corresponding lexer.
        """
        self.lexer = lexer

    def check(self, expected: Union[List[TokenKind], TokenKind]) -> bool:
        """
        Check that the next token is of a given kind. If a list of n TokenKinds
        is given, check that the next n TokenKinds match the next expected
        ones.

        :param expected: The kind of the token we expect or a list of expected
                         token kinds if we look ahead more than one token at
                         a time.
        :returns: True if the next token has the expected token kind, False
                 otherwise.
        """

        if isinstance(expected, list):
            tokens = self.lexer.peek(len(expected))
            assert isinstance(tokens, list), "List of tokens expected"
            return all(
                [tok.kind == type_ for tok, type_ in zip(tokens, expected)])

        token = self.lexer.peek()
        assert isinstance(token, Token), "Single token expected"
        return token.kind == expected

    def match(self, expected: TokenKind, call_from=None) -> Token:

        if self.check(expected):
            token = self.lexer.peek()
            assert isinstance(token, Token), "A single token expected"
            self.lexer.consume()
            return token

        token = self.lexer.peek()
        assert isinstance(token, Token), "A single token expected"
        
        self.report_error(token, NOT_FOUND.format(expected=expected))

    def report_error(self, token : Token, msg : str):
        self.print_syntax_err(token)
        print(msg)
        self.print_err_line(token)
        exit(0)

    def print_syntax_err(self, token : Token):
        print(f"SyntaxError (line {token.line+1}, column {token.col+1}): ",end='')

    def print_err_line(self, token : Token ):
        
        for char in self.lexer.tokenizer.scanner.file_content_by_line[token.line]:
            print(char, end='')

        if self.lexer.tokenizer.scanner.file_content_by_line[token.line][-1] != '\n':
            print()

        print('-' * token.col + "^")


    def parse_input(self):
        """
            input := regSpec Newline program
        """
        regs : List[int] = self.parse_reg_spec()
        
        self.match(TokenKind.NEWLINE)

        labels : Dict[str, int] = None
        instrs : List[Instr] = None
        (labels, instrs) = self.parse_program()

        self.match(TokenKind.EOF)

        return ((regs, labels, instrs))

    def parse_reg_spec(self):
        """
            `registers` (number)*
        """
        self.match(TokenKind.REGISTERS_SYMBOL)
        regs = []
        while self.check(TokenKind.INTEGER):
            regs.append(self.match(TokenKind.INTEGER).value)
        return regs

    def parse_program(self):
        """
            program := (labInst NEWLINE)*
            labInst := (label `:`)? inst
            instr := `inc` register
                   | `decjz` register label
            register := `r` number
        """
        instructions = []
        labels = {}
        while self.is_labInst_first_set():
            label, instr = self.parse_labInst()
            instructions.append(instr)

            # if label is already defined, raise exception
            if label in labels:
                raise("label define again")
            else:
                labels[label] = len(instructions) - 1
            self.match(TokenKind.NEWLINE)

        return (labels, instructions)
    
    def is_labInst_first_set(self):
        if self.check(TokenKind.DECJZ) or self.check(TokenKind.INC) or self.check(TokenKind.IDENTIFIER):
            return True
        else: return False

    def parse_labInst(self) -> Tuple[str, Instr]:
        pass
