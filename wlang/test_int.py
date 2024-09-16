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
    def test_one(self):
        prg1 = "x := 10; print_state"
        # test parser
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        self.assertIsNotNone(st)
        # x is defined
        self.assertIn("x", st.env)
        # x is 10
        self.assertEquals(st.env["x"], 10)
        # no other variables in the state
        self.assertEquals(len(st.env), 1)
    
    # Test havocstmt in int.py
    def test_havoc(self):
        prg1 = "havoc x; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        self.assertIsNotNone(st)
        # x is defined
        self.assertIn("x", st.env)
        # no other variables in the state
        self.assertEquals(len(st.env), 1)
        self.assertIsNotNone(st.env["x"],0)
    
    
    def test_ifstmtskip(self):
        prg1 = "x:= 10; if x < 10 then l:=1; if x <= 10 then i:= 1; if x>13 then skip else j:= 1; if x<11 then skip else k:= 1; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("i", st.env)
        self.assertIn("j", st.env)
        self.assertNotIn("k", st.env)
        self.assertNotIn("l", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["i"], 1)
        self.assertEquals(st.env["j"], 1)
        self.assertEquals(len(st.env), 3)
    
    #def test_ifnotelsestmt(self):
    #    prg1 = "x:= 10; if x < 10 then i:=1; print_state"
    #    ast1 = ast.parse_string(prg1)
    #    print(ast1)
    #    print(repr(ast1))
    #    interp = int.Interpreter()
    #    st = int.State()
    #    st = interp.run(ast1, st)
    #    print(st)
    #    self.assertIsNotNone(st)
    #    self.assertIn("x", st.env)
    #    self.assertNotIn("i", st.env)
    #    self.assertEquals(st.env["x"], 10)
    #    self.assertEquals(len(st.env), 1)
        
    def test_while(self):
        prg1 = "x:= 10; while x>0 do x:= x-1; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertEquals(st.env["x"], 0)
        self.assertEquals(len(st.env), 1)
        
    def test_RelExp(self):
        prg1 = "x:=10 ; y:= 5; z:= 10; if x=z then i:=1; if x>=y then j:=1; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("y", st.env)
        self.assertIn("z", st.env)
        self.assertIn("i", st.env)
        self.assertIn("j", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["y"], 5)
        self.assertEquals(st.env["z"], 10)
        self.assertEquals(st.env["i"], 1)
        self.assertEquals(st.env["j"], 1)
        self.assertEquals(len(st.env), 5)
        
    def test_Aexp(self):
        prg1 = "x:=10 ; y:=5 ; i:= x+y; j:= x-y; k:= x*y; l:= x/y; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("y", st.env)
        self.assertIn("i", st.env)
        self.assertIn("j", st.env)
        self.assertIn("k", st.env)
        self.assertIn("l", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["y"], 5)
        self.assertEquals(st.env["j"], 5)
        self.assertEquals(st.env["k"], 50)
        self.assertEquals(st.env["l"], 2)
        self.assertEquals(len(st.env), 6)
    
    def test_Bexp(self):
        prg1 = "x:=10; if not x=10 then i:=1 else j:=1; if x=10 and x>5 then k:=1; if x=10 or x>5 then l:=1; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertNotIn("i", st.env)
        self.assertIn("j", st.env)
        self.assertIn("k", st.env)
        self.assertIn("l", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["j"], 1)
        self.assertEquals(st.env["k"], 1)
        self.assertEquals(st.env["l"], 1)
        self.assertEquals(len(st.env), 4)
    
    
    def test_assumetrue(self):
        prg1 = "x:=10 ; assume(x>5); i:=1 ;print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("i", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["i"], 1)
        self.assertEquals(len(st.env), 2)
    
    def test_assumefalse(self):
        i=5
        try:
            prg1 = "x:=10 ; assume(x<5); i:=1 ;print_state"
            ast1 = ast.parse_string(prg1)
            print(ast1)
            print(repr(ast1))
            interp = int.Interpreter()
            st = int.State()
            st = interp.run(ast1, st)
        except:
            i=2
        self.assertEquals(i,2)
    
    ## Ast file tests ##
    
    def test_stmtlist(self):
        prg1 ="x:=10 ; y:=20"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("y", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["y"], 20)
        self.assertTrue(ast1==ast1)
        self.assertEquals(len(st.env), 2)
    
    def test_skipstmtlist(self):
        prg1 ="skip"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertTrue(ast1==ast1)
    
    def test_printstmt(self):
        prg1 ="print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertTrue(ast1==ast1)
    
    def test_printheap(self):
        prg1 ="ref y := 42; x := &y; z := *x; print_heap; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNone(st)
        self.assertTrue(ast1==ast1)
    
    def test_assgnstmt(self):
        prg1 ="x:=10"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertTrue(ast1==ast1)
        self.assertEquals(len(st.env), 1)
    
    def test_havocstmt(self):
        prg1 = "havoc x, y; print_state"
        prg2 = "havoc x, y; print_state"
        ast1 = ast.parse_string(prg1)
        ast2 = ast.parse_string(prg2)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("y", st.env)
        self.assertEqual(ast1,ast2)
        self.assertEquals(len(st.env), 2)
    
    def test_ifstmt(self):
        prg1 ="x:=10; if x>15 then j:=1 else i:=1"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("i", st.env)
        self.assertNotIn("j", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["i"], 1)
        self.assertTrue(ast1.stmts[1]==ast1.stmts[1])
        self.assertEquals(len(st.env), 2)
    
    def test_whilestmt(self):
        prg1 ="{x:=10};while x>0 do x:= x-1"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertEquals(st.env["x"], 0) 
        self.assertTrue(ast1.stmts[1]==ast1.stmts[1])
        self.assertEquals(len(st.env), 1)
    
    def test_assertstmt(self):
        prg1 = "x := 5; assert (x > 0); print_state"
        prg2 = "x := 5; assert (x > 0); print_state"
        ast1 = ast.parse_string(prg1)
        ast2 = ast.parse_string(prg2)
        self.assertEqual(ast1,ast2)
        
    def test_assumestmt(self):
        prg1 = "x := 5; assume (x > 0); skip"
        prg2 = "x := 5; assume (x > 0); skip"
        ast1 = ast.parse_string(prg1)
        ast2 = ast.parse_string(prg2)
        self.assertEqual(ast1,ast2)
    
    
    def test_expstmt(self):
        expr = ast.Exp(["-", "+"],[10,5])
        self.assertTrue(expr.is_binary())
        
    def test_conststmt(self):
        prg2 = "10"
        var = ast.Const(prg2)
        print(var)
        print(repr(var))
        umap = {}
        umap[var] = 1
    
    def test_intstmt(self):
        prg2 = "10"
        var = ast.IntVar(prg2)
        print(var)
        print(repr(var))
        umap = {}
        umap[var] = 1
        
    def test_boolstmt(self):
        prg1 = "x:=10 ; y:=10; if true and false then skip else print_state"
        ast1 = ast.parse_string(prg1)
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(ast1)
        print(repr(ast1))
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertIn("y", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(st.env["y"], 10)
        self.assertEquals(len(st.env), 2)
        
        
    def test_filestmt(self):
        ast1 = ast.parse_file("wlang/test1.prg")
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        self.assertIsNotNone(st)
        self.assertIn("x", st.env)
        self.assertEquals(st.env["x"], 10)
        self.assertEquals(len(st.env), 1)
     
    def test_rexp(self):
        prg1 = "x := 10"
        ast1 = ast.parse_string(prg1)
        interp = int.Interpreter()
        st = int.State()
        st.__repr__()
        st = interp.run(ast1, st)
        
    ## Parser file tests ##
    
    
    
    def test_WLSerror(self):
        sem_par = parser.WhileLangSemantics()
        prg1 = "x := 10; print_state"
        ast1 = ast.parse_string(prg1)
        self.assertEquals(sem_par.start(ast1),ast1)
        #self.assertRaises(parser.WLSyntaxError,sem_par.visit,ast1)
    
    def test_WLSwhile(self):
        sem_par = parser.WhileLangSemantics()
        prg1 = "x := 10; while x < 0 inv false do x := x-1; print_state"
        ast1 = ast.parse_string(prg1)
        self.assertEquals(sem_par.while_stmt(ast1),ast1)
    
    def test_WLSbfact(self):
        sem_par = parser.WhileLangSemantics()
        prg1 = "{x:=10 ; y:=20}; if x=y then i:=1 else skip"
        ast1 = ast.parse_string(prg1)
        self.assertEquals(sem_par.bfactor(ast1),ast1)
    
    def test_WLSnegnum(self):
        sem_par = parser.WhileLangSemantics()
        prg1 = "x := 3; y := -3; c:= x-y; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertEquals (st.env['x'], 3)
        self.assertEquals (st.env['y'], -3)
        self.assertEquals (st.env['c'], 6)
        self.assertEquals (len(st.env), 3)
        self.assertEquals(sem_par.neg_number(ast1),ast1)
        
    def test_WLSbterm(self):
        sem_par = parser.WhileLangSemantics()
        expr = ast.Exp("+",["-","+","*"])
        self.assertEquals(sem_par.bterm(expr),expr)
    # Cant test __NEWLINE__ in parser.py
    #def test_WSLnewline(self):
    #    sem_par = parser.WhileLangParser()
    #    prg1 = "x := 10 \n y := 20 \r z:= 30 \u000C print_state"
    #    ast1 = ast.parse_string(prg1)
    #    print("Ast for newline")
    #    print(ast1)
    #    self.assertEquals(sem_par.NEWLINE(ast1),ast1)

    
    def test_WLSall(self):
        sem_par = parser.WhileLangSemantics()
        prg1 = "{x:=28; y:=24}\u000C; if x=y then i:=1 else skip\n\r; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        interp = int.Interpreter()
        st = int.State()
        st = interp.run(ast1, st)
        print(st)
        self.assertIsNotNone(st)
        self.assertEquals(st.env['x'], 28)
        self.assertEquals(st.env['y'], 24)
        self.assertNotIn('i', st.env)
        self.assertEquals(len(st.env), 2)
        self.assertEquals(sem_par.stmt_list(ast1),ast1)
        self.assertEquals(sem_par.stmt(ast1),ast1)
        self.assertEquals(sem_par.asgn_stmt(ast1),ast1)
        self.assertEquals(sem_par.skip_stmt(ast1),ast1)
        self.assertEquals(sem_par.block_stmt(ast1),ast1)
        self.assertEquals(sem_par.print_state_stmt(ast1),ast1)
        self.assertEquals(sem_par.assume_stmt(ast1),ast1)
        self.assertEquals(sem_par.assert_stmt(ast1),ast1)
        self.assertEquals(sem_par.havoc_stmt(ast1),ast1)
        self.assertEquals(sem_par.if_stmt(ast1),ast1)
        self.assertEquals(sem_par.var_list(ast1),ast1)
        self.assertEquals(sem_par.bexp(ast1),ast1)
        self.assertEquals(sem_par.bterm(ast1),ast1)
        self.assertEquals(sem_par.batom(ast1),ast1)
        self.assertEquals(sem_par.bool_const(ast1),ast1)
        self.assertEquals(sem_par.rexp(ast1),ast1)
        self.assertEquals(sem_par.rop(ast1),ast1)
        self.assertEquals(sem_par.aexp(ast1),ast1)
        self.assertEquals(sem_par.addition(ast1),ast1)
        self.assertEquals(sem_par.subtraction(ast1),ast1)
        self.assertEquals(sem_par.term(ast1),ast1)
        self.assertEquals(sem_par.mult(ast1),ast1)
        self.assertEquals(sem_par.division(ast1),ast1)
        self.assertEquals(sem_par.factor(ast1),ast1)
        self.assertEquals(sem_par.atom(ast1),ast1)
        self.assertEquals(sem_par.name(ast1),ast1)
        self.assertEquals(sem_par.INT(ast1),ast1)
        self.assertEquals(sem_par.NAME(ast1),ast1)
        self.assertEquals(sem_par.NEWLINE(ast1),ast1)
        self.assertEquals(sem_par.number(ast1),ast1)
        
        
class ast_visitor(ast.AstVisitor):
    def __init__(self):
        super(ast_visitor, self).__init__()
       
    def visit_StmtList(self,node,*args,**kwargs):
        for stmt in node.stmts:
            self.visit(stmt)
    
    def visit_Stmt(self,node,*args,**kwargs):
        pass
    
    def visit_AsgnStmt(self,node,*args,**kwargs):
        super().visit_AsgnStmt(node,*args,**kwargs)
        super().visit_IntVar(node,*args,**kwargs)
    
    def visit_Exp(self,node,*args,**kwargs):
        pass
    
    #def visit_Const(self,node,*args,**kwargs):
    #    pass
    
    
        
class Test_ast_visitor(unittest.TestCase):
    def test_intvar(self):
        prg1 = "x := 10"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)

    def test_skip(self):
        prg1 = "skip"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_print(self):
        prg1 = "print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_if(self):
        prg1 = "x:=10; if x=15 then skip else j:=1"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_while(self):
        prg1 = "x:=10; while true do j:=1"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_assgn(self):
        prg1 = "x:=10"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_assert(self):
        prg1 = "assert x > 0; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_assume(self):
        prg1 = "assume x > 0; skip"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_havoc(self):
        prg1 = "havoc x"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        print(repr(ast1))
        av = ast_visitor()
        av.visit(ast1)
    
    def test_printemp(self):
        av = ast_visitor()
    
    def test_printstmtlst(self):
        ast1 = ast.StmtList([])
        av = ast.PrintVisitor()
        av.visit_StmtList(ast1)
        
    
    
    
    