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

# from unittest.mock import patch, MagicMock

from . import ast, sym, int
from .sym import main

import sys
from io import StringIO

# Additional Imports
import z3

# Helper Function to initialize environment for all Test cases
def init_environment( program ):
    prg1 = program
    ast1 = ast.parse_string(prg1)
    engine = sym.SymExec()
    st = sym.SymState()
    out = [s for s in engine.run(ast1, st)]

    return out

def capture_output_string(args):
    sys.argv = args
    op = StringIO()
    sys.stdout = op
    sym.main()
    sys.stdout = sys.__stdout__
    op.seek(0)
    op_str = op.read()

    return op_str


class TestSym (unittest.TestCase):
    def test_one(self):
        prg1 = "havoc x; assume x > 10; assert x > 15"
        ast1 = ast.parse_string(prg1)
        engine = sym.SymExec()
        st = sym.SymState()
        out = [s for s in engine.run(ast1, st)]
        self.assertEquals(len(out), 1)

    # @patch('sys.exit')
    # def test_sys_exit(self, mock_exit):
    #     # Mock sys.exit to prevent actual termination
    #     mock_exit.side_effect = MagicMock()
        
    #     # Call the main function
    #     from .sym import main
    #     sym.main()
        
    #     # python3 -m wlang.sym wlang/test1.prg

    def test_main_with_output_states(self):
        '''
        Coverage reached 99% with this test,
        Discussed with billy that lines like `sys.exit(main())` aren't considered while evaluation
        Only lines not covered:
        line 310 : Discussed with Billy, this maybe a bug, 
                   since an infinite loop in wlang/test2.prg outputs:
                   [symexec]: found 0 symbolic states 
        Line 322 :  it is sys.exit(main()) 
        '''
        output_str = capture_output_string(['sym.py', 'wlang/test1.prg'])
        self.assertIn('[symexec]: symbolic state reached', output_str)
        self.assertIn('[symexec]: found 1 symbolic state', output_str)
    
    def test_prg2_with_output_states(self):
        # output_str = capture_output_string()
        sys.argv = ['int.py', 'wlang/test2.prg']
        op = StringIO()
        sys.stdout = op
        int.main()
        sys.stdout = sys.__stdout__
        op.seek(0)
        op_str = op.read()
        self.assertIn('Heap:', op_str)

    def test_smt2(self):
        out = out = init_environment( "havoc x; assume x > 10; assert x > 15" )
        self.assertEquals(len(out), 1)
        self.assertIsNotNone(out[0].to_smt2())
        self.assertIsNotNone(out[0].pick_concerete())

    def test_AExp(self):
        out = init_environment( "havoc x; y := x + 3; assume x > 10; assert y > 15; print_state; skip" )
        self.assertEquals(len(out), 1)

    def test_rel_Exp(self):
        out = init_environment( "havoc x; y := x + 2; assert y >= x; z := x - 1; assert x > z; w := x; assert w = x" )
        self.assertEquals(len(out), 1)

    def test_bool_exp(self):
        out = init_environment( "havoc x; assume x > 0; if x < 0 or false then x := x + 1" )
        self.assertEquals(len(out), 1)
        self.assertIsNotNone(out[0].pick_concerete())

    # Extend your answer to symbolic execution of programs with if-statements;
    def test_if(self):
        out = init_environment( "havoc x, y; if (x > 0 and y < 0) then x := x / 2 else y := y * 2; assume y > x" )
        self.assertEquals(len(out), 1)
    
    def test_if_nested(self):
        out = init_environment("havoc x; assume x > 0; if x > 0 then if x > 5 then y := 2 else y := 3 else y := 4")
        self.assertEquals(len(out), 2)

    def test_if_not_else(self):
        out = init_environment( "havoc x; assume x > 0; if not x <= 0 then x := x + 1 else x := x - 1" )
        self.assertEquals(len(out), 1)

    # Extend your answer to symbolic execution of programs with while-statements. To handle arbitrary loops,
    # assume that the loop is executed at most 10 times. That is, your symbolic execution engine should explore all
    # feasible program paths in which the body of each loop is executed no more than 10 times.
    def test_while_ten(self):
        out = init_environment( "havoc x; while x > 0 do x := x - 1" )
        self.assertEquals(len(out), 11)
        
    def test_while_must_into_loop(self):
        out = init_environment("havoc x; assume x > 0; y := x + 1; while y > x do y := y - 1")
        self.assertEquals(len(out), 1)

    def test_nested_while(self):
        out = init_environment("x := 2; z := 0; while x > 0 do {y := 2; while y > 0 do {z := z + 1; y := y - 1}; x := x - 1}")
        self.assertEquals(len(out), 1)

    # Combo of While-if
    def test_ifwhile(self):
        out = init_environment("havoc x; if x > 0 then {y := 2; while y > 0 do y := y - 1} else skip")
        self.assertEquals(len(out), 2)

    def test_whileif(self):
        out = init_environment( "x := 2; havoc y; while x > 0 do {if y < x then y := y + 1 else y := y - 1; x := x - 1}" )
        self.assertEquals(len(out), 3)
    
    # 4) e) Provide a program on which your symbolic execution engine diverges (i.e., takes longer than a few seconds to run).
    # TEST 1: Take too long to run 
    # def test_while_symbolic_execution_engine_diverges(self):
    #     out = init_environment( "havoc x, y, z; while x > 0 do {while y > x do {while z > y do {z := z / 2 - 1}; y := y / 2 - 1}; x := x / 2 - 1}" )
    #     self.assertEquals(len(out), 726)

    # TEST 2: 
    # def test_while_symbolic_execution_engine_diverges(self):
    #     out = init_environment( "havoc x, y; while x > 0 do {while y > x do {y := y / 2}; x := x - 1}" )
    #     self.assertEquals(len(out), 406)