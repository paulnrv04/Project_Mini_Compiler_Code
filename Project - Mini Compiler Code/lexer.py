import re
from enum import Enum, auto

class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    # Specific operator types matching the parser's expectations
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto() 
    MULTIPLY = auto()
    DIVIDE = auto()
    LT = auto() # Less Than
    GT = auto() # Greater Than
    LE = auto() # Less Than or Equal
    GE = auto() # Greater Than or Equal
    LPAREN = auto() 
    RPAREN = auto()
    SEMICOLON = auto() # Semicolon
    BOOLEAN = auto() # For 'true'/'false' literals
    CHAR = auto() # For single character literals
    
    # Keeping a generic OPERATOR for any other potential operators not explicitly listed
    # If you don't have other operators, this can be removed.
    OPERATOR = auto() 
    
    EOF = auto()

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

class Lexer:
    def __init__(self, code):
        self.code = code
        self.keywords = {'if', 'else', 'then', 'while', 'do'}

    def tokenize(self):
        patterns = {
            'WHITESPACE': r'\s+',          
            'STRING': r'"[^"\n]*"',        
            'CHAR': r"'[^'\n]'",           
            'BOOLEAN': r'\b(true|false)\b', 
            'NUMBER': r'\d+(\.\d+)?',              
            'IDENTIFIER': r'[a-zA-Z_]\w*', 
            # Specific operators matching the new TokenType enum
            'ASSIGN': r'=',
            'PLUS': r'\+',
            'MINUS': r'-',
            'MULTIPLY': r'\*',
            'DIVIDE': r'/',
            'LE': r'<=', 
            'GE': r'>=', 
            'LT': r'<',  
            'GT': r'>',  
            'LPAREN': r'\(' ,              
            'RPAREN': r'\)',               
            'SEMICOLON': r';',             
        }
        
        # Sort patterns by length of regex string (descending) to prioritize longer matches
        # (e.g., '<=' must be matched before '<')
        sorted_patterns = sorted(patterns.items(), key=lambda item: len(item[1]), reverse=True)
        token_regex = '|'.join(f'(?P<{k}>{v})' for k, v in sorted_patterns if v)
        
        tokens = []
        current_pos = 0 

        for match in re.finditer(token_regex, self.code):
            kind = match.lastgroup
            value = match.group()
            
            if match.start() > current_pos:
                raise SyntaxError(f"Illegal character: '{self.code[current_pos]}'"
                                  f" at position {current_pos}")
            
            if kind == 'WHITESPACE':
                pass 
            elif kind == 'IDENTIFIER' and value in self.keywords:
                tokens.append(Token(TokenType.KEYWORD, value))
            elif kind == 'STRING':
                tokens.append(Token(TokenType.STRING, value.strip('"')))
            elif kind == 'CHAR':
                tokens.append(Token(TokenType.CHAR, value.strip("'"))) 
            elif kind == 'BOOLEAN':
                tokens.append(Token(TokenType.BOOLEAN, int(value == 'true'))) 
            elif kind == 'ASSIGN':
                tokens.append(Token(TokenType.ASSIGN, value))
            elif kind == 'PLUS':
                tokens.append(Token(TokenType.PLUS, value))
            elif kind == 'MINUS':
                tokens.append(Token(TokenType.MINUS, value))
            elif kind == 'MULTIPLY':
                tokens.append(Token(TokenType.MULTIPLY, value))
            elif kind == 'DIVIDE':
                tokens.append(Token(TokenType.DIVIDE, value))
            elif kind == 'LT':
                tokens.append(Token(TokenType.LT, value))
            elif kind == 'GT':
                tokens.append(Token(TokenType.GT, value))
            elif kind == 'LE':
                tokens.append(Token(TokenType.LE, value))
            elif kind == 'GE':
                tokens.append(Token(TokenType.GE, value))
            elif kind == 'LPAREN':
                tokens.append(Token(TokenType.LPAREN, value))
            elif kind == 'RPAREN':
                tokens.append(Token(TokenType.RPAREN, value))
            elif kind == 'SEMICOLON': 
                tokens.append(Token(TokenType.SEMICOLON, value))
            else:
                tokens.append(Token(TokenType[kind], value)) 
            
            current_pos = match.end() 
        
        if current_pos < len(self.code):
            raise SyntaxError(f"Illegal character: '{self.code[current_pos]}'"
                              f" at position {current_pos}")

        tokens.append(Token(TokenType.EOF, '')) 
        return tokens

