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

import io 
import z3

from . import ast, int

# Additional imports
from functools import reduce

def return_state_and_dict(kwargs):
    return kwargs["states"], dict(kwargs)

class SymState(object):
    def __init__(self, solver=None):
        # environment mapping variables to symbolic constants
        self.env = dict()
        # path condition
        self.path = list()
        self._solver = solver
        if self._solver is None:
            self._solver = z3.Solver()

        # true if this is an error state
        self._is_error = False

    def add_pc(self, *exp):
        """Add constraints to the path condition"""
        self.path.extend(exp)
        self._solver.append(exp)

    def is_error(self):
        return self._is_error

    def mk_error(self):
        self._is_error = True

    def is_empty(self):
        """Check whether the current symbolic state has any concrete states"""
        res = self._solver.check()
        return res == z3.unsat

    def pick_concerete(self):
        """Pick a concrete state consistent with the symbolic state.
           Return None if no such state exists"""
        res = self._solver.check()
        if res != z3.sat:
            return None
        model = self._solver.model()
        st = int.State()
        for (k, v) in self.env.items():
            st.env[k] = model.eval(v)
        return st

    def fork(self):
        """Fork the current state into two identical states that can evolve separately"""
        child = SymState()
        child.env = dict(self.env)
        child.add_pc(*self.path)

        return (self, child)

    def __repr__(self):
        return str(self)

    def to_smt2(self):
        """Returns the current state as an SMT-LIB2 benchmark"""
        return self._solver.to_smt2()

    def __str__(self):
        buf = io.StringIO()
        for k, v in self.env.items():
            buf.write(str(k))
            buf.write(': ')
            buf.write(str(v))
            buf.write('\n')
        buf.write('pc: ')
        buf.write(str(self.path))
        buf.write('\n')

        return buf.getvalue()


class SymExec(ast.AstVisitor):
    def __init__(self):
        pass

    def run(self, ast, state):
        # set things up and
        # call self.visit (ast, state=state)
        return self.visit(ast, states=[state])

    def visit_IntVar(self, node, *args, **kwargs):
        return kwargs['states'].env[node.name]

    def visit_BoolConst(self, node, *args, **kwargs):
        return z3.BoolVal(node.val)

    def visit_IntConst(self, node, *args, **kwargs):
        return z3.IntVal(node.val)

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

    def visit_BExp(self, node, *args, **kwargs):
        l = [self.visit(a, *args, **kwargs) for a in node.args]

        if node.op == "not":
            assert node.is_unary()
            assert len(l) == 1
            return z3.Not(l[0])

        base = None
        def fn_and(x, y):
            return z3.And(x, y)
        def fn_or(x, y):
            return z3.Or(x, y)

        if node.op == "and":
            base = True
            return reduce(fn_and, l, base)
        elif node.op == "or":
            base = False
            return reduce(fn_or, l, base)

    def visit_AExp(self, node, *args, **kwargs):
        l = [self.visit(a, *args, **kwargs) for a in node.args]

        def fn_plus(x, y):
            return x+y
        def fn_minus(x, y):
            return x-y
        def fn_mul(x, y):
            return x*y
        def fn_div(x, y):
            return x/y

        if node.op == "+":
            return reduce(fn_plus, l)
        elif node.op == "-":
            return reduce(fn_minus, l)
        elif node.op == "*":
            return reduce(fn_mul, l)
        elif node.op == "/":
            return reduce(fn_div, l)

    def visit_SkipStmt(self, node, *args, **kwargs):
        return kwargs["states"]

    def visit_PrintStateStmt(self, node, *args, **kwargs):
        print(kwargs["states"])
        return kwargs["states"]

    def visit_AsgnStmt(self, node, *args, **kwargs):
        states, nkwargs = return_state_and_dict(kwargs)
        for st in states:
            nkwargs['states'] = st
            st.env[node.lhs.name] = self.visit(node.rhs, *args, **nkwargs)
        return states

    def visit_IfStmt(self, node, *args, **kwargs):
        states, nkwargs = return_state_and_dict(kwargs)
        res1, res2 = [], []
        for st in states:
            nkwargs["states"] = st
            cond = self.visit(node.cond, *args, **nkwargs)
            state_1, state_2 = st.fork()
            state_1.add_pc(cond)
            state_2.add_pc(z3.Not(cond))
            if not state_1.is_empty():
                res1.append(state_1)
            if not state_2.is_empty():
                res2.append(state_2)
        
        res = []
        if len(res1) > 0:
            nkwargs["states"] = res1
            res.extend(self.visit(node.then_stmt, *args, **nkwargs))

        if len(res2) > 0:
            if node.has_else():
                nkwargs["states"] = res2
                res.extend(self.visit(node.else_stmt, *args, **nkwargs))
            else:
                res.extend(res2)

        return res

    def visit_WhileStmt(self, node, *args, **kwargs):
        states, nkwargs = return_state_and_dict(kwargs)
        res = []
        for i in range(11):
            res1, res2 = [], []
            for state in states:
                nkwargs["states"] = state
                cond = self.visit(node.cond, *args, **nkwargs)
                s1, s2 = state.fork()
                s1.add_pc(cond)
                s2.add_pc(z3.Not(cond))
                if not s1.is_empty():
                    res1.append(s1)
                if not s2.is_empty():
                    res2.append(s2)
            
            res.extend(res2)
            if len(res1) == 0:
                break
            nkwargs["states"] = res1
            states = self.visit(node.body, *args, **nkwargs)

        return res

    def visit_AssertStmt(self, node, *args, **kwargs):
        # Don't forget to print an error message if an assertion might be violated
        states, nkwargs = return_state_and_dict(kwargs)
        res = []
        for state in states:
            nkwargs["states"] = state
            cond = self.visit(node.cond, *args, **nkwargs)
            state_1, state_2 = state.fork()
            state_1.add_pc(z3.Not(cond))
            state_2.add_pc(cond)
            # Catching error assertion
            if not state_1.is_empty():
                state_1.mk_error()
                state_1.is_error()
                print("Assertion Violation")
            if not state_2.is_empty():
                res.append(state_2)
        return res

    def visit_AssumeStmt(self, node, *args, **kwargs):
        states, nkwargs = return_state_and_dict(kwargs)
        res = []
        for state in states:
            nkwargs["states"] = state
            cond = self.visit(node.cond, *args, **nkwargs)
            state.add_pc(cond)
            if not state.is_empty():
                res.append(state)
            else:
                state.pick_concerete()
        return res

    def visit_HavocStmt(self, node, *args, **kwargs):
        states = kwargs["states"]
        for state in states:
            for var in node.vars:
                state.env[var.name] = z3.FreshInt(var.name)
        return states

    def visit_StmtList(self, node, *args, **kwargs):
        state, nkwargs = return_state_and_dict(kwargs)
        for statement in node.stmts:
            nkwargs["states"] = state
            state = self.visit(statement, *args, **nkwargs)
        return state

def _parse_args():
    import argparse
    ap = argparse.ArgumentParser(prog='sym',
                                 description='WLang Interpreter')
    ap.add_argument('in_file', metavar='FILE',
                    help='WLang program to interpret')
    args = ap.parse_args()
    return args


def main():
    args = _parse_args()
    prg = ast.parse_file(args.in_file)
    st = SymState()
    sym = SymExec()

    states = sym.run(prg, st)
    if states is None:
        print('[symexec]: no output states')
    else:
        count = 0
        for out in states:
            count = count + 1
            print('[symexec]: symbolic state reached')
            print(out)
        print('[symexec]: found', count, 'symbolic states')
    return 0


if __name__ == '__main__':
    sys.exit(main())
