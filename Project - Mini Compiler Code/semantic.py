from parser import AssignNode, VarNode, BinOpNode, IfNode, WhileNode, BlockNode, StringNode, NumberNode

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node, in_loop=False):
        if isinstance(node, AssignNode):
            self.analyze(node.value)
            self.symbol_table[node.name] = self.infer_type(node.value)

        elif isinstance(node, VarNode):
            if node.name not in self.symbol_table:
                raise Exception(f"Semantic Error: Undefined variable '{node.name}'")

        elif isinstance(node, BinOpNode):
            self.analyze(node.left)
            self.analyze(node.right)

        elif isinstance(node, IfNode):
            self.analyze(node.condition)
            self.analyze(node.then_branch, in_loop=in_loop)
            if node.else_branch:
                self.analyze(node.else_branch, in_loop=in_loop)

        elif isinstance(node, WhileNode):
            self.analyze(node.condition)
            self.analyze(node.body, in_loop=True)

        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                self.analyze(stmt, in_loop=in_loop)

    def infer_type(self, node):
        if isinstance(node, NumberNode):
            return 'int'
        elif isinstance(node, StringNode):
            return 'string'
        elif isinstance(node, VarNode):
            return self.symbol_table.get(node.name, 'unknown')
        return 'unknown'