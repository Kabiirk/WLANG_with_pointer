import unittest
import sys
from . import ast, stats_visitor


class TestStatsVisitor(unittest.TestCase):
    def test_one(self):
        prg1 = "x := 10; print_state"
        ast1 = ast.parse_string(prg1)

        sv = stats_visitor.StatsVisitor()
        sv.visit(ast1)
        # UNCOMMENT to run the test
        self.assertEquals(sv.get_num_stmts(), 2)
        self.assertEquals(sv.get_num_vars(), 1)

    def test_havoc(self):
        prg1 = "havoc x; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        sv =stats_visitor.StatsVisitor()
        sv.visit(ast1)
        self.assertEquals(sv.get_num_stmts(), 2)
        self.assertEquals(sv.get_num_vars(),1)
    
    def test_assert(self):
        prg1 = "assert x>0; print_state"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        sv =stats_visitor.StatsVisitor()
        sv.visit(ast1)
        self.assertEquals(sv.get_num_stmts(), 2)
        self.assertEquals(sv.get_num_vars(),1)
    
    def test_assume(self):
        prg1 = "x:=10 ; assume x>0"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        sv =stats_visitor.StatsVisitor()
        sv.visit(ast1)
        self.assertEquals(sv.get_num_stmts(), 2)
        self.assertEquals(sv.get_num_vars(),1)
    
    def test_while(self):
        prg1 = "x:=10 ; while x>0 do x:=x-1 "
        ast1 = ast.parse_string(prg1)
        print(ast1)
        sv =stats_visitor.StatsVisitor()
        sv.visit(ast1)
        self.assertEquals(sv.get_num_stmts(), 3)
        self.assertEquals(sv.get_num_vars(),1)
    
    def test_if(self):
        prg1 = "x:=10 ; if x>0 then x:=x-1 else x:=x+1"
        ast1 = ast.parse_string(prg1)
        print(ast1)
        sv =stats_visitor.StatsVisitor()
        sv.visit(ast1)
        self.assertEqual(sv.get_num_stmts(), 4)
        self.assertEqual(sv.get_num_vars(),1)
    
    #def test_file(self):
    #    ast1 = ast.parse_file(sys.argv[1])
    #    print(ast1)
    #    print(repr(ast1))
    #    sv =stats_visitor.StatsVisitor()
    #    sv.visit(ast1)
    #    self.assertEqual(sv.get_num_stmts(), 2)
    #    self.assertEqual(sv.get_num_vars(),1)
        