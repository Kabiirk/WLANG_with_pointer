import unittest

from . import ast, undef_visitor


class TestUndefVisitor(unittest.TestCase):
    def test1(self):
        prg1 = "x := 10; y := x + z"
        ast1 = ast.parse_string(prg1)

        uv = undef_visitor.UndefVisitor()
        uv.check(ast1)
        # UNCOMMENT to run the test
        self.assertEquals (set ([ast.IntVar('z')]), uv.get_undefs ())
    
    def test_undef_if(self):
        prg1 = "if x>0 then x:= x + 1; if x<0 then skip else y:=x+2"
        ast1 = ast.parse_string(prg1)
        uv = undef_visitor.UndefVisitor()
        uv.check(ast1)
        self.assertEquals (set ([ast.IntVar('x')]), uv.get_undefs ())
    
    def test_undef_while(self):
        prg1 = "while x>0 do x:= x + 1"
        ast1 = ast.parse_string(prg1)
        uv = undef_visitor.UndefVisitor()
        uv.check(ast1)
        self.assertEquals (set ([ast.IntVar('x')]), uv.get_undefs ())

    def test_undef_havoc(self):
        prg1 = "havoc x; y:=z+1"
        ast1 = ast.parse_string(prg1)
        uv = undef_visitor.UndefVisitor()
        uv.check(ast1)
        self.assertEquals (set ([ast.IntVar('z')]), uv.get_undefs ())
        
    def test_undef_assert(self):
        prg1 = "assert x>0"
        ast1 = ast.parse_string(prg1)
        uv = undef_visitor.UndefVisitor()
        uv.check(ast1)
        self.assertEquals (set ([ast.IntVar('x')]), uv.get_undefs ())
    
    def test_undef_assume(self):
        prg1 = "assume x>0"
        ast1 = ast.parse_string(prg1)
        uv = undef_visitor.UndefVisitor()
        uv.check(ast1)
        self.assertEquals (set ([ast.IntVar('x')]), uv.get_undefs ())