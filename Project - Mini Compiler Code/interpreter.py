from parser import (
    NumberNode, VarNode, AssignNode, BinOpNode, IfNode, WhileNode,
    BlockNode, StringNode
)

class Interpreter:
    def __init__(self, symbol_table, input_func=None):
        self.env = {} # this is a storage for variables (like a dictionary)
        self.symbol_table = symbol_table # stores extra info about variables, types, etc.
        self.input_func = input_func if input_func is not None else input # Default to built-in input if not provided

    def eval(self, node):
        if isinstance(node, BlockNode):
            result = None
            for stmt in node.statements:
                result = self.eval(stmt)
            return result

        elif isinstance(node, NumberNode):
            try:
                # Try float first
                num = float(node.value)
                # Convert to int if it has no decimal part
                return int(num) if num.is_integer() else num
            except ValueError:
                print(f"Semantic Error: Invalid number '{node.value}'")
                return None


        elif isinstance(node, VarNode):
            # Retrieve variable value from environment
            if node.name not in self.env:
                print(f"Semantic Error: Undefined variable '{node.name}'")
                return None
            return self.env[node.name]

        elif isinstance(node, StringNode):
            return node.value

        elif isinstance(node, AssignNode):
            # Evaluate the right-hand side expression
            value = self.eval(node.value)
            if value is None:
                return None # Propagate error if value evaluation failed
            
            # Assign the value to the variable in the environment
            self.env[node.name] = value
            return value # Assignment typically returns the assigned value

        elif isinstance(node, BinOpNode):
            left = self.eval(node.left)
            right = self.eval(node.right)

            if left is None or right is None:
                return None # Propagate error if operand evaluation failed

            # Type checking for arithmetic operations
            if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                print(f"Semantic Error: Invalid operand types for operator '{node.op}': {type(left).__name__} and {type(right).__name__}")
                return None

            # Perform the binary operation
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                if right == 0:
                    print("Runtime Error: Division by zero")
                    return None
                return left / right # Integer division as per common compiler behavior
            elif node.op == '<':
                return int(left < right) # Return 1 for true, 0 for false
            elif node.op == '>':
                return int(left > right)
            elif node.op == '<=':
                return int(left <= right)
            elif node.op == '>=':
                return int(left >= right)
            else:
                print(f"Runtime Error: Unknown operator '{node.op}'")
                return None

        elif isinstance(node, IfNode):
            condition_value = self.eval(node.condition)
            if condition_value is None:
                return None # Propagate error if condition evaluation failed

            # Apply your custom truthiness rule: > 0 is true, <= 0 is false
            if condition_value > 0:
                return self.eval(node.then_branch)
            elif node.else_branch:
                return self.eval(node.else_branch)
            return None # If no else branch and condition is false

        elif isinstance(node, WhileNode):
            loop_limit = 10 
            count = 0
            while self.eval(node.condition):
                result = self.eval(node.body)
                print("Result:", result)
                count += 1
                if count >= loop_limit:
                    print("Loop limit reached (10 iterations). Breaking loop to prevent infinite execution.")
                    break
            return result

        else:
            print(f"Runtime Error: Unknown AST node type: {type(node).__name__}")
            return None

    def get_formatted_env(self):
        return self.env
