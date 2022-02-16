from atexit import register
from lexer import Token, TokenKind, Lexer
from typing import List, Optional, Union, Tuple, Dict
from errmsg import *
from instr import *

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
            instr = self.parse_labInst()
            instructions.append(instr)

            # if label is already defined, raise exception
            label = instr.label
            if label == None:
                pass
            elif label in labels:
                raise Exception("label define again")
            else:
                labels[label] = len(instructions) - 1
            
            self.match(TokenKind.NEWLINE)

        return (labels, instructions)
    
    def is_labInst_first_set(self):
        if self.check(TokenKind.DECJZ) or self.check(TokenKind.INC) or self.check(TokenKind.IDENTIFIER):
            return True
        else: return False

    def parse_labInst(self) -> Instr:
        """
          labInst := (label `:`)? inst
            instr := `inc` register
                   | `decjz` register label
         register := `r` number
        """
        if self.check(TokenKind.IDENTIFIER): 
            label = self.match(TokenKind.IDENTIFIER) 
            self.match(TokenKind.COLON)
        else:
            label = None
        instr = self.parse_instr()
        instr.label = label
        return instr


    def parse_instr(self) -> Instr:
        if self.check(TokenKind.INC):
            self.match(TokenKind.INC)
            reg = self.match(TokenKind.REGISTER).value
            return Instr(Opcode.INC, [reg])
        elif self.check(TokenKind.DECJZ):
            self.match(TokenKind.DECJZ)
            reg = self.match(TokenKind.REGISTER).value
            target_branch = self.match(TokenKind.IDENTIFIER).value
            return Instr(Opcode.DECJZ, [reg, target_branch])
        else:
            raise Exception("unmatch")