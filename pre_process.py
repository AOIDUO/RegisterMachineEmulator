import io
import os
from typing import List

from frontend import Lexer, Parser, TokenKind, Token

def pre_process(f, replace_label_with_addr=False):
    lines = f.readlines()
    stream = io.StringIO(''.join(lines))
    parser = Parser(Lexer(stream))
    alias_macro_map = {}
    
    # read all lines starting with "IMPORT"
    # and also read macros
    while parser.check(TokenKind.IMPORT):
        parser.match(TokenKind.IMPORT)
        dir = parser.match(TokenKind.DIRECTORY).value
        parser.match(TokenKind.AS)
        alias = parser.match(TokenKind.IDENTIFIER).value
        parser.match(TokenKind.NEWLINE)

        if not os.path.isabs(dir):
            dir = os.path.join(os.getcwd(), dir)
        macro_content,_,_ = pre_process(open(dir,mode='r'), replace_label_with_addr=True)
        alias_macro_map[alias] = (dir,macro_content)
    
    # chop off import haeding
    line_of_registers_symbol = parser.lexer.peek().line
    lines = lines[line_of_registers_symbol:]
        
    return lines, io.StringIO(''.join(lines)), alias_macro_map

