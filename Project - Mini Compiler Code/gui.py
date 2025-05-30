import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter


class InterpreterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini.Compiler")
        self.root.geometry("1000x700")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.load_example_code()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create paned window for resizable sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for code input
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right panel for output and results
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def setup_left_panel(self, parent):
        # Code input section
        code_label = ttk.Label(parent, text="Enter your sample code:", font=('Arial', 10, 'bold'))
        code_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Code text area with syntax highlighting placeholder
        self.code_text = scrolledtext.ScrolledText(
            parent, 
            height=20, 
            font=('Consolas', 11),
            wrap=tk.NONE,
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white',
            selectbackground='#264f78'
        )
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        self.run_button = ttk.Button(
            button_frame, 
            text="Run Code", 
            command=self.run_code,
            style='Accent.TButton'
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_code
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.example_button = ttk.Button(
            button_frame, 
            text="Load Example", 
            command=self.load_example_code
        )
        self.example_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            parent, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def setup_right_panel(self, parent):
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Output tab
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Output")
        
        output_label = ttk.Label(output_frame, text="Program Output:", font=('Arial', 10, 'bold'))
        output_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            font=('Consolas', 10),
            state=tk.DISABLED,
            bg='#f8f8f8',
            fg='#333333'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tokens tab
        tokens_frame = ttk.Frame(notebook)
        notebook.add(tokens_frame, text="Tokens")
        
        tokens_label = ttk.Label(tokens_frame, text="Lexical Analysis - Tokens:", font=('Arial', 10, 'bold'))
        tokens_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tokens_text = scrolledtext.ScrolledText(
            tokens_frame,
            height=10,
            font=('Consolas', 9),
            state=tk.DISABLED,
            bg='#f0f8ff',
            fg='#333333'
        )
        self.tokens_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # AST tab
        ast_frame = ttk.Frame(notebook)
        notebook.add(ast_frame, text="Parser")
        
        ast_label = ttk.Label(ast_frame, text="Abstract Syntax Tree:", font=('Arial', 10, 'bold'))
        ast_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.ast_text = scrolledtext.ScrolledText(
            ast_frame,
            height=10,
            font=('Consolas', 9),
            state=tk.DISABLED,
            bg='#f0fff0',
            fg='#333333'
        )
        self.ast_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Variables tab
        vars_frame = ttk.Frame(notebook)
        notebook.add(vars_frame, text="Variables")
        
        vars_label = ttk.Label(vars_frame, text="Variable Environment:", font=('Arial', 10, 'bold'))
        vars_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Create treeview for variables
        self.vars_tree = ttk.Treeview(vars_frame, columns=('Value', 'Type'), show='tree headings')
        self.vars_tree.heading('#0', text='Variable')
        self.vars_tree.heading('Value', text='Value')
        self.vars_tree.heading('Type', text='Type')
        
        self.vars_tree.column('#0', width=150)
        self.vars_tree.column('Value', width=100)
        self.vars_tree.column('Type', width=80)
        
        vars_scrollbar = ttk.Scrollbar(vars_frame, orient=tk.VERTICAL, command=self.vars_tree.yview)
        self.vars_tree.configure(yscrollcommand=vars_scrollbar.set)
        
        self.vars_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vars_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def clear_code(self):
        self.code_text.delete(1.0, tk.END)
        self.clear_output_panels()
        self.status_var.set("Code cleared")
        
    def clear_output_panels(self):
        # Clear all output panels
        for text_widget in [self.output_text, self.tokens_text, self.ast_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
        
        # Clear variables tree
        for item in self.vars_tree.get_children():
            self.vars_tree.delete(item)
    
    def load_example_code(self):
        example_code = '''// Simple arithmetic and variables
    x = 10;
    y = 20;
    sum = x + y;

// Conditional statement
    if sum > 25 then
        result = sum * 2
    else
        result = sum / 2;

// Loop example
    counter = 0;
    while counter < 3 do
        counter = counter + 1;
'''
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, example_code)
        self.status_var.set("Example code loaded")
    
    def update_text_widget(self, widget, content):
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, str(content))
        widget.config(state=tk.DISABLED)
    
    def update_variables_tree(self, env):
        # Clear existing items
        for item in self.vars_tree.get_children():
            self.vars_tree.delete(item)
        
        # Add variables to tree
        for var_name, value in env.items():
            var_type = type(value).__name__
            self.vars_tree.insert('', tk.END, text=var_name, values=(value, var_type))
    
    def run_code_thread(self, code):
        try:
            self.status_var.set("Tokenizing...")
            self.root.update()
            
            # Lexical Analysis
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # Update tokens display
            tokens_str = '\n'.join(str(token) for token in tokens)
            self.root.after(0, lambda: self.update_text_widget(self.tokens_text, tokens_str))
            
            self.status_var.set("Parsing...")
            self.root.update()
            
            # Syntax Analysis
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Update AST display
            ast_str = self.format_ast(ast, 0)
            self.root.after(0, lambda: self.update_text_widget(self.ast_text, ast_str))
            
            self.status_var.set("Semantic analysis...")
            self.root.update()
            
            # Semantic Analysis
            semantic = SemanticAnalyzer()
            semantic.analyze(ast)
            
            self.status_var.set("Interpreting...")
            self.root.update()
            
            # Interpretation with output capture
            output_capture = io.StringIO()
            
            with redirect_stdout(output_capture), redirect_stderr(output_capture):
                interpreter = Interpreter(semantic.symbol_table)
                result = interpreter.eval(ast)
                
                if result is not None:
                    print(f"Final Result: {result}")
            
            # Update output display
            output_str = output_capture.getvalue()
            self.root.after(0, lambda: self.update_text_widget(self.output_text, output_str))
            
            # Update variables display
            self.root.after(0, lambda: self.update_variables_tree(interpreter.get_formatted_env()))
            
            self.status_var.set("Execution Completed Successfully")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.update_text_widget(self.output_text, error_msg))
            self.status_var.set(f"Error: {type(e).__name__}")
            
        finally:
            # Re-enable the run button
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
    
    def format_ast(self, node, indent=0):
        """Format AST for display with proper indentation"""
        indent_str = "  " * indent
        
        if hasattr(node, 'statements'):  # BlockNode
            result = f"{indent_str}Block:\n"
            for stmt in node.statements:
                result += self.format_ast(stmt, indent + 1)
            return result
        elif hasattr(node, 'condition') and hasattr(node, 'then_branch'):  # IfNode
            result = f"{indent_str}If:\n"
            result += f"{indent_str}  Condition:\n{self.format_ast(node.condition, indent + 2)}"
            result += f"{indent_str}  Then:\n{self.format_ast(node.then_branch, indent + 2)}"
            if node.else_branch:
                result += f"{indent_str}  Else:\n{self.format_ast(node.else_branch, indent + 2)}"
            return result
        elif hasattr(node, 'condition') and hasattr(node, 'body'):  # WhileNode
            result = f"{indent_str}While:\n"
            result += f"{indent_str}  Condition:\n{self.format_ast(node.condition, indent + 2)}"
            result += f"{indent_str}  Body:\n{self.format_ast(node.body, indent + 2)}"
            return result
        elif hasattr(node, 'name') and hasattr(node, 'value'):  # AssignNode
            result = f"{indent_str}Assignment:\n"
            result += f"{indent_str}  Variable: {node.name}\n"
            result += f"{indent_str}  Value:\n{self.format_ast(node.value, indent + 2)}"
            return result
        elif hasattr(node, 'left') and hasattr(node, 'right'):  # BinOpNode
            result = f"{indent_str}BinaryOp ({node.op}):\n"
            result += f"{indent_str}  Left:\n{self.format_ast(node.left, indent + 2)}"
            result += f"{indent_str}  Right:\n{self.format_ast(node.right, indent + 2)}"
            return result
        else:
            return f"{indent_str}{repr(node)}\n"
    
    def run_code(self):
        code = self.code_text.get(1.0, tk.END).strip()
        
        if not code:
            messagebox.showwarning("Warning", "Please enter some code to execute.")
            return
        
        # Clear previous results
        self.clear_output_panels()
        
        # Disable run button during execution
        self.run_button.config(state=tk.DISABLED)
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.run_code_thread, args=(code,))
        thread.daemon = True
        thread.start()


def main():
    root = tk.Tk()
    
    # Set application icon (if you have one)
    try:
        root.iconbitmap('icon.ico')  # Optional: add an icon file
    except:
        pass
    
    app = InterpreterGUI(root)
    
    # Handle window closing
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()


if __name__ == '__main__':
    main()