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

import unittest

from . import ast, int, parser


class TestInt(unittest.TestCase):
    def test_ref1(self):
        prg1 = "ref x:=42; y := *x ; print_state"
        ast1 = ast.parse_string(prg1)
        interp = int.Interpreter()
        state = int.State()
        interp.run(ast1, state)
        self.assertEquals(state.env['y'], 42)

    def test_ref2(self):
        prg1 = "ref y:=42; x := &y ; z := *x ; print_state"
        ast1 = ast.parse_string(prg1)
        interp = int.Interpreter()
        state = int.State()
        interp.run(ast1, state)
        self.assertEquals(state.env['z'], 42)
    
    def test_pointer_decl_stmt_equality(self):
        stmt1 = ast.PointerDeclStmt(ast.IntVar('x'), ast.IntConst(42))
        stmt2 = ast.PointerDeclStmt(ast.IntVar('x'), ast.IntConst(42))
        stmt3 = ast.PointerDeclStmt(ast.IntVar('y'), ast.IntConst(42))
        stmt4 = ast.PointerDeclStmt(ast.IntVar('x'), ast.IntConst(43))

        self.assertEqual(stmt1, stmt2)  # should be equal
        self.assertNotEqual(stmt1, stmt3)  # different lhs
        self.assertNotEqual(stmt1, stmt4)  # different rhs

    def test_address_of_uninitialized_variable(self):
        prg = "x := &y ; print_state"
        ast1 = ast.parse_string(prg)
        interp = int.Interpreter()
        state = int.State()
        with self.assertRaises(KeyError):
            interp.run(ast1, state)

    def test_dereference_uninitialized_pointer(self):
        prg = "y := *x ; print_state"
        ast1 = ast.parse_string(prg)
        interp = int.Interpreter()
        state = int.State()
        with self.assertRaises(KeyError):
            interp.run(ast1, state)

    def test_dereference_pointer_with_uninitialized_address(self):
        prg = "ref x := 42; z := *y ; print_state"
        ast1 = ast.parse_string(prg)
        interp = int.Interpreter()
        state = int.State()
        state.env['y'] = 123456  # Simulate a pointer to an uninitialized address
        with self.assertRaises(KeyError):
            interp.run(ast1, state)
    
    def test_visit_pointer_decl_stmt(self):
        stmt = ast.PointerDeclStmt(ast.IntVar('x'), ast.IntConst(42))
        visitor = ast.AstVisitor()
        result = visitor.visit(stmt)
        self.assertIsInstance(result, type(None))

    def test_visit_pointer_deref_stmt(self):
        stmt = ast.PointerDerefStmt(ast.IntVar('x'), ast.IntVar('y'))
        visitor = ast.AstVisitor()
        result = visitor.visit(stmt)
        self.assertIsInstance(result, type(None))

    def test_visit_address_of(self):
        expr = ast.AddressOf(ast.IntVar('x'))
        visitor = ast.AstVisitor()
        result = visitor.visit(expr)
        self.assertIsInstance(result, type(None))
        
    def test_address_of_equality(self):
        addr1 = ast.AddressOf(ast.IntVar('x'))
        addr2 = ast.AddressOf(ast.IntVar('x'))
        addr3 = ast.AddressOf(ast.IntVar('y'))

        self.assertEqual(addr1, addr2)  # should be equal
        self.assertNotEqual(addr1, addr3)  # different vars
        
    def test_pointer_deref_stmt_equality(self):
        stmt1 = ast.PointerDerefStmt(ast.IntVar('x'), ast.IntVar('y'))
        stmt2 = ast.PointerDerefStmt(ast.IntVar('x'), ast.IntVar('y'))
        stmt3 = ast.PointerDerefStmt(ast.IntVar('a'), ast.IntVar('y'))
        stmt4 = ast.PointerDerefStmt(ast.IntVar('x'), ast.IntVar('b'))

        self.assertEqual(stmt1, stmt2)  # should be equal
        self.assertNotEqual(stmt1, stmt3)  # different lhs
        self.assertNotEqual(stmt1, stmt4)  # different rhs
