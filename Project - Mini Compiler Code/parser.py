from lexer import TokenType, Token # Ensure Token is also imported from lexer

class ASTNode: pass

class NumberNode(ASTNode):
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Number({self.value})"

class VarNode(ASTNode):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Var({self.name})"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"BinOp({self.left} {self.op} {self.right})"

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self): return f"Assign({self.name} = {self.value})"

class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"If({self.condition}, Then: {self.then_branch}" + \
               (f", Else: {self.else_branch})" if self.else_branch else ")")

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self): return f"While({self.condition}, Do: {self.body})"

class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return f"Block({self.statements})"

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self): return f"String('{self.value}')"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None) 

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return Token(TokenType.EOF, None)

    def consume(self):
        self.pos += 1

    def match(self, expected_type, expected_value=None):
        token = self.current()
        if token.type == expected_type and (expected_value is None or token.value == expected_value):
            self.consume()
            return token
        raise SyntaxError(f"Unexpected token: {token} at position {self.pos}. Expected type {expected_type}" + (f" with value '{expected_value}'" if expected_value else ""))

    def parse(self):
        statements = []
        while self.current().type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
        return BlockNode(statements)

    def parse_statement(self):
        token = self.current()
        if token.type == TokenType.KEYWORD:
            if token.value == 'if':
                stmt = self.parse_if()
            elif token.value == 'while':
                stmt = self.parse_while()
            else:
                raise SyntaxError(f"Unexpected keyword: {token} at position {self.pos}")
        else:
            stmt = self.parse_expression()
        
        if self.current().type == TokenType.SEMICOLON:
            self.consume()
        
        return stmt

    def parse_if(self):
        self.match(TokenType.KEYWORD, 'if')
        # Removed self.match(TokenType.LPAREN) and self.match(TokenType.RPAREN)
        # to allow conditions without parentheses.
        condition = self.parse_expression() 

        self.match(TokenType.KEYWORD, 'then')
        then_branch = self.parse_statement()
        
        else_branch = None
        if self.current().type == TokenType.KEYWORD and self.current().value == 'else':
            self.consume()
            if self.current().type == TokenType.KEYWORD and self.current().value == 'if':
                else_branch = self.parse_if()
            else:
                else_branch = self.parse_statement()
        return IfNode(condition, then_branch, else_branch)

    def parse_while(self):
        self.match(TokenType.KEYWORD, 'while')
        # Removed self.match(TokenType.LPAREN) and self.match(TokenType.RPAREN)
        # to allow conditions without parentheses.
        condition = self.parse_expression() 

        self.match(TokenType.KEYWORD, 'do')
        body = self.parse_statement()
        return WhileNode(condition, body)

    def parse_expression(self):
        node = self.parse_comparison()

        while self.current().type == TokenType.ASSIGN:
            self.consume()
            right_side = self.parse_expression() 
            
            if not isinstance(node, VarNode):
                raise SyntaxError(f"Invalid assignment target: Cannot assign to {type(node).__name__}. Must be a variable.")
            
            node = AssignNode(node.name, right_side)
        
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current().type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_token = self.current() 
            self.consume()            
            op = op_token.value       
            right = self.parse_term()
            node = BinOpNode(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.current() 
            self.consume()            
            op = op_token.value       
            right = self.parse_factor()
            node = BinOpNode(node, op, right)
        return node

    def parse_factor(self):
        token = self.current()
        if token.type == TokenType.PLUS or token.type == TokenType.MINUS:
            op_token = self.current() 
            self.consume()            
            op = op_token.value       
            right = self.parse_factor() 
            return BinOpNode(NumberNode(0), op, right) 
        
        node = self.parse_atom()
        while self.current().type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self.current() 
            self.consume()            
            op = op_token.value       
            right = self.parse_atom()
            node = BinOpNode(node, op, right)
        return node

    def parse_atom(self):
        token = self.current()
        if token.type == TokenType.NUMBER:
            self.consume()
            return NumberNode(token.value)
        elif token.type == TokenType.IDENTIFIER:
            self.consume()
            return VarNode(token.value)
        elif token.type == TokenType.STRING:
            self.consume()
            return StringNode(token.value)
        elif token.type == TokenType.BOOLEAN:
            self.consume()
            return NumberNode(token.value)
        elif token.type == TokenType.CHAR:
            self.consume()
            return StringNode(token.value)
        elif token.type == TokenType.LPAREN:
            self.consume()
            node = self.parse_expression()
            self.match(TokenType.RPAREN)
            return node
        
        raise SyntaxError(f"Unexpected token in expression: {token} at position {self.pos}")

