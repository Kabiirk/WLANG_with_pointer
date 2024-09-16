# The MIT License (MIT)
# Copyright (c) 2016 Arie Gurfinkel

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
from functools import reduce
from io import StringIO

from . import ast,int,parser


class State(object):
    def __init__(self):
        self.env = dict()
        super().__init__()

    def __repr__(self):
        repr(self.env)

    def __str__(self):
        buf = StringIO()
        for k, v in self.env.items():
            buf.write(str(k))
            buf.write(": ")
            buf.write(str(v))
            buf.write("\n")

        return buf.getvalue()


class Interpreter(ast.AstVisitor):
    def __init__(self):
        self.heap = {} # Heap is created for storing addresses of the references of the pointers
        super().__init__()

    def run(self, ast, state):
        return self.visit(ast, state=state)

    def visit_IntVar(self, node, *args, **kwargs):
        return kwargs["state"].env[node.name]

    def visit_Const(self, node, *args, **kwargs):
        return node.val

    def visit_RelExp(self, node, *args, **kwargs):
        lhs = self.visit(node.arg(0), *args, **kwargs)
        rhs = self.visit(node.arg(1), *args, **kwargs)
        if node.op == "<=":
            return lhs <= rhs
        if node.op == "<":
            return lhs < rhs
        if node.op == "=":
            return lhs == rhs
        if node.op == ">=":
            return lhs >= rhs
        if node.op == ">":
            return lhs > rhs

        assert False

    def visit_BExp(self, node, *args, **kwargs):
        kids = [self.visit(a, *args, **kwargs) for a in node.args]

        if node.op == "not":
            assert node.is_unary()
            assert len(kids) == 1
            return not kids[0]

        fn = None
        base = None
        if node.op == "and":
            fn = lambda x, y: x and y
            base = True
        elif node.op == "or":
            fn = lambda x, y: x or y
            base = False

        assert fn is not None
        return reduce(fn, kids, base)

    def visit_AExp(self, node, *args, **kwargs):
        kids = [self.visit(a, *args, **kwargs) for a in node.args]

        fn = None

        if node.op == "+":
            fn = lambda x, y: x + y

        elif node.op == "-":
            fn = lambda x, y: x - y

        elif node.op == "*":
            fn = lambda x, y: x * y

        elif node.op == "/":
            fn = lambda x, y: x / y

        assert fn is not None
        return reduce(fn, kids)

    def visit_SkipStmt(self, node, *args, **kwargs):
        return kwargs["state"]

    def visit_PrintStateStmt(self, node, *args, **kwargs):
        print(kwargs["state"])
        return kwargs["state"]

    def visit_PrintHeapStmt(self, node, *args, **kwargs):
        print("Heap: ", self.heap)
        # return kwargs["state"]

    def visit_AsgnStmt(self, node, *args, **kwargs):
        st = kwargs["state"]
        st.env[node.lhs.name] = self.visit(node.rhs, *args, **kwargs)
        return st

    def visit_IfStmt(self, node, *args, **kwargs):
        cond = self.visit(node.cond, *args, **kwargs)
        if cond:
            return self.visit(node.then_stmt, *args, **kwargs)
        else:
            if node.has_else():
                return self.visit(node.else_stmt, *args, **kwargs)
            else:
                return kwargs["state"]

    def visit_WhileStmt(self, node, *args, **kwargs):
        cond = self.visit(node.cond, *args, **kwargs)

        if cond:
            # execute the body
            st = self.visit(node.body, *args, **kwargs)
            # execute the loop again
            kwargs["state"] = st
            return self.visit(node, *args, **kwargs)
        else:
            # loop condition is false, don't execute the body
            return kwargs["state"]

    def visit_AssertStmt(self, node, *args, **kwargs):
        cond = self.visit(node.cond, *args, **kwargs)
        if not cond:
            assert False, "Assertion error: " + str(node)
        return kwargs["state"]

    def visit_AssumeStmt(self, node, *args, **kwargs):
        return self.visit_AssertStmt(node, *args, **kwargs)

    def visit_StmtList(self, node, *args, **kwargs):
        st = kwargs["state"]

        nkwargs = dict(kwargs)
        for stmt in node.stmts:
            nkwargs["state"] = st
            st = self.visit(stmt, *args, **nkwargs)
        return st

    def visit_HavocStmt(self, node, *args, **kwargs):
        st = kwargs["state"]
        for v in node.vars:
            # assign 0 as the default value
            st.env[v.name] = 0
        return st

    # The visit method for the PointerDeclStmt and PointerDerefStmt is implemented
    # Here the heap is used to store the address of the reference of the pointer

    def visit_AddressOf(self, node, *args, **kwargs):
        st = kwargs["state"]
        var_name = node.var.name
        if var_name not in st.env:
            raise KeyError(f"Variable '{var_name}' is not initialized")
        address = st.env[var_name]
        print(f"Address of {var_name}: {address}")
        return address  # Return the address of the variable

    def visit_PointerDeclStmt(self, node, *args, **kwargs):
        st = kwargs["state"]
        value = self.visit(node.rhs, *args, **kwargs)
        address = id(value)  # Use id to simulate a memory address
        self.heap[address] = value  # Store the value in the heap
        st.env[node.lhs.name] = address  # Initialize the pointer in the state
        print(f"Pointer declared {node.lhs.name} with value {value} at address {address}")
        return st

    def visit_PointerDerefStmt(self, node, *args, **kwargs):
        st = kwargs["state"]
        if node.rhs.name not in st.env:
            raise KeyError(f"Pointer '{node.rhs.name}' is not initialized in the state")
        
        address = st.env[node.rhs.name]
        if address not in self.heap:
            raise KeyError(f"Address '{address}' is not initialized in the heap")
        
        st.env[node.lhs.name] = self.heap[address]
        print(f"Dereferencing pointer {node.rhs.name} with address {address} to value {self.heap[address]}")
        return st

def _parse_args():
    import argparse

    ap = argparse.ArgumentParser(prog="int", description="WLang Interpreter")
    ap.add_argument("in_file", metavar="FILE", help="WLang program to run")
    args = ap.parse_args()
    return args


def main():
    args = _parse_args()
    prg = ast.parse_file(args.in_file)
    st = State()
    interp = Interpreter()
    interp.run(prg, st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
