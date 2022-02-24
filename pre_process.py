import io
import os
from typing import List

from frontend import Lexer, Parser, TokenKind, Token

def pre_process(f, replace_label_with_addr=False):
    lines = f.readlines()
    stream = io.StringIO(''.join(lines))
    parser = Parser(Lexer(stream))
    
    if parser.check(TokenKind.IMPORT):
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
            macro_content,_ = pre_process(open(dir,mode='r'), replace_label_with_addr=True)
            alias_macro_map[alias] = (dir,macro_content)
        
        # chop off import haeding
        line_of_registers_symbol = parser.lexer.peek().line
        lines = lines[line_of_registers_symbol:]
        
        '''
        # another replacement method
        line_index = 0
        while line_index < len(lines):
            lexer = Lexer(io.StringIO(lines[line_index]))
            token = lexer.consume()

            # if the line has lable, ignore it
            if lexer.peek().kind == TokenKind.COLON:
                lexer.consume()
                token = lexer.consume()

            # if it is a macro
            if token.kind == TokenKind.IDENTIFIER and token.value in alias_macro_map:
                alias = token.value
                new_line = ''.join(alias_macro_map[alias][1])
                param_count = 0
                token = lexer.consume()
                while token.kind != TokenKind.NEWLINE:
                    if token.kind == TokenKind.REGISTER:
                        new_line = new_line.replace(f"${param_count}", f"r{token.value}")
                    else:
                        new_line = new_line.replace(f"${param_count}", token.value)
                    param_count += 1
                    token = lexer.consume()


                lines[i] = new_line + '\n'

            pass
        '''

        # replacement
        for i in range(len(lines)):
            lexer = Lexer(io.StringIO(lines[i]))
            token = lexer.consume()

            if lexer.peek().kind == TokenKind.COLON:
                lexer.consume()
                token = lexer.consume()

            if token.kind == TokenKind.IDENTIFIER and token.value in alias_macro_map:
                alias = token.value
                new_line = ''.join(alias_macro_map[alias][1])
                param_count = 0
                token = lexer.consume()
                while token.kind != TokenKind.NEWLINE:
                    if token.kind == TokenKind.REGISTER:
                        new_line = new_line.replace(f"${param_count}", f"r{token.value}")
                    else:
                        new_line = new_line.replace(f"${param_count}", str(token.value))
                    param_count += 1
                    token = lexer.consume()


                lines[i] = new_line + '\n'



    if replace_label_with_addr :
        parser = Parser(Lexer(io.StringIO(''.join(lines))), is_macro=True)
        (labels, instrs) = parser.parse_program()

        for i in range(len(lines)):
            lexer = Lexer(io.StringIO(lines[i]))
            token = lexer.consume()

            if lexer.peek().kind == TokenKind.COLON:
                colon_token = lexer.consume()
                lines[i] = lines[i][colon_token.col+1:]
                token = lexer.consume()

            if token.kind == TokenKind.DECJZ:
                token = lexer.peek(2)[1]
                line_in_macro = token.line
                if token.kind == TokenKind.IDENTIFIER:
                    if token.value in labels:
                        lines[i] = lines[i].replace(token.value, str(labels[token.value]))
                    else:
                        raise Exception("undefined label")
                else:
                    pass
                    # print(token.kind)
                    # if token.kind == TokenKind.INTEGER:
                        # print(line_in_macro + i)
                        # lines[i] = lines[i].replace(str(token.value), str(line_in_macro + i))
        # print(labels)
        print(lines)

    return lines, io.StringIO(''.join(lines))

