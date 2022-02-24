import io
import os
from frontend import Lexer, Parser, TokenKind

def pre_process(f):
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
            x,_ = pre_process(open(dir,mode='r'))
            alias_macro_map[alias] = (dir,x)
        
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

        return lines, io.StringIO(''.join(lines))
    else: 
        return lines, io.StringIO(''.join(lines))

