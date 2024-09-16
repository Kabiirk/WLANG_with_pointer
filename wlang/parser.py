#!/usr/bin/env python

# CAVEAT UTILITOR
#
# This file was automatically generated by TatSu.
#
#    https://pypi.python.org/pypi/tatsu/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.

from __future__ import annotations

import sys

from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu
from tatsu.parsing import leftrec, nomemo, isname # noqa
from tatsu.infos import ParserConfig
from tatsu.util import re, generic_main  # noqa


KEYWORDS = {}  # type: ignore


class WhileLangBuffer(Buffer):
    def __init__(self, text, /, config: ParserConfig = None, **settings):
        config = ParserConfig.new(
            config,
            owner=self,
            whitespace=None,
            nameguard=None,
            comments_re=None,
            eol_comments_re='#[^\\r\\n]*',
            ignorecase=False,
            namechars='',
            parseinfo=False,
        )
        config = config.replace(**settings)
        super().__init__(text, config=config)


class WhileLangParser(Parser):
    def __init__(self, /, config: ParserConfig = None, **settings):
        config = ParserConfig.new(
            config,
            owner=self,
            whitespace=None,
            nameguard=None,
            comments_re=None,
            eol_comments_re='#[^\\r\\n]*',
            ignorecase=False,
            namechars='',
            parseinfo=False,
            keywords=KEYWORDS,
            start='start',
        )
        config = config.replace(**settings)
        super().__init__(config=config)

    @tatsumasu()
    def _start_(self):  # noqa
        self._stmt_list_()

    @tatsumasu()
    def _stmt_list_(self):  # noqa

        def sep0():
            self._token(';')

        def block0():
            self._stmt_()
        self._positive_gather(block0, sep0)

    @tatsumasu()
    def _stmt_(self):  # noqa
        with self._choice():
            with self._option():
                self._skip_stmt_()
            with self._option():
                self._asgn_stmt_()
            with self._option():
                self._block_stmt_()
            with self._option():
                self._if_stmt_()
            with self._option():
                self._while_stmt_()
            with self._option():
                self._assert_stmt_()
            with self._option():
                self._assume_stmt_()
            with self._option():
                self._havoc_stmt_()
            with self._option():
                self._print_state_stmt_()
            with self._option():
                self._pointer_decl_stmt_() # Added pointer decl stmt ( ref )
            with self._option():
                self._pointer_deref_stmt_() # Added pointer deref stmt ( * )
            with self._option():
                self._print_heap_stmt_()
            self._error(
                'expecting one of: '
                "'assert' 'assume' 'havoc' 'if'"
                "'print_state' 'print_heap' 'skip' 'while' '{'"
                '<asgn_stmt> <assert_stmt> <assume_stmt>'
                '<block_stmt> <havoc_stmt> <if_stmt>'
                '<name> <print_state_stmt> <print_heap_stmt> <skip_stmt>'
                '<while_stmt> <pointer_decl_stmt> <pointer_deref_stmt>' # Added pointer decl and deref stmt
            )

    # Added pointer decl stmt method and generated the nodes for the stmt
    @tatsumasu()
    def _pointer_decl_stmt_(self):
        self._token('ref')
        self._name_()
        self.name_last_node('lhs')
        self._token(':=')
        self._aexp_()
        self.name_last_node('rhs')
        self._define(
            ['lhs', 'rhs'],
            []
        )
    # Added pointer deref stmt method and generated the nodes for the stmt
    @tatsumasu()
    def _pointer_deref_stmt_(self):
        self._name_()
        self.name_last_node('lhs')
        self._token(':=')
        self._token('*')
        self._name_()
        self.name_last_node('rhs')
        self._define(
            ['lhs', 'rhs'],
            []
        )

    @tatsumasu()
    def _asgn_stmt_(self):  # noqa
        self._name_()
        self.name_last_node('lhs')
        self._token(':=')
        self._aexp_()
        self.name_last_node('rhs')

        self._define(
            ['lhs', 'rhs'],
            []
        )

    @tatsumasu()
    def _block_stmt_(self):  # noqa
        self._token('{')
        self._stmt_list_()
        self.name_last_node('@')
        self._token('}')

    @tatsumasu()
    def _skip_stmt_(self):  # noqa
        self._token('skip')

    @tatsumasu()
    def _print_state_stmt_(self):  # noqa
        self._token('print_state')

    # Added print heap stmt method to generate node for print_heap command
    @tatsumasu()
    def _print_heap_stmt_(self):  # noqa
        self._token('print_heap')

    @tatsumasu()
    def _if_stmt_(self):  # noqa
        self._token('if')
        self._cut()
        self._bexp_()
        self.name_last_node('cond')
        self._token('then')
        self._stmt_()
        self.name_last_node('then_stmt')
        with self._optional():
            self._token('else')
            self._stmt_()
            self.name_last_node('else_stmt')

            self._define(
                ['else_stmt'],
                []
            )

        self._define(
            ['cond', 'else_stmt', 'then_stmt'],
            []
        )

    @tatsumasu()
    def _while_stmt_(self):  # noqa
        self._token('while')
        self._bexp_()
        self.name_last_node('cond')
        with self._optional():
            self._token('inv')
            self._bexp_()
            self.name_last_node('inv')

            self._define(
                ['inv'],
                []
            )
        self._token('do')
        self._stmt_()
        self.name_last_node('body')

        self._define(
            ['body', 'cond', 'inv'],
            []
        )

    @tatsumasu()
    def _assert_stmt_(self):  # noqa
        self._token('assert')
        self._bexp_()
        self.name_last_node('cond')

        self._define(
            ['cond'],
            []
        )

    @tatsumasu()
    def _assume_stmt_(self):  # noqa
        self._token('assume')
        self._bexp_()
        self.name_last_node('cond')

        self._define(
            ['cond'],
            []
        )

    @tatsumasu()
    def _havoc_stmt_(self):  # noqa
        self._token('havoc')
        self._var_list_()
        self.name_last_node('vars')

        self._define(
            ['vars'],
            []
        )

    @tatsumasu()
    def _var_list_(self):  # noqa

        def sep0():
            self._token(',')

        def block0():
            self._name_()
        self._positive_gather(block0, sep0)

    @tatsumasu()
    def _bexp_(self):  # noqa

        def sep0():
            with self._group():
                self._token('or')
                self.name_last_node('op')

        def block0():
            self._bterm_()
            self.name_last_node('args')
        self._positive_gather(block0, sep0)

    @tatsumasu()
    def _bterm_(self):  # noqa

        def sep0():
            with self._group():
                self._token('and')
                self.name_last_node('op')

        def block0():
            self._bfactor_()
            self.name_last_node('args')
        self._positive_gather(block0, sep0)

    @tatsumasu()
    def _bfactor_(self):  # noqa
        with self._choice():
            with self._option():
                self._batom_()
                self.name_last_node('arg')
            with self._option():
                self._token('not')
                self.name_last_node('op')
                self._cut()
                self._batom_()
                self.name_last_node('arg')

                self._define(
                    ['arg', 'op'],
                    []
                )
            self._error(
                'expecting one of: '
                "'(' 'not' <batom> <bool_const> <rexp>"
            )

    @tatsumasu()
    def _batom_(self):  # noqa
        with self._choice():
            with self._option():
                self._rexp_()
            with self._option():
                self._bool_const_()
            with self._option():
                self._token('(')
                self._bexp_()
                self.name_last_node('@')
                self._token(')')
            self._error(
                'expecting one of: '
                "'(' 'false' 'true' <aexp> <bool_const>"
                '<rexp>'
            )

    @tatsumasu()
    def _bool_const_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('true')
            with self._option():
                self._token('false')
            self._error(
                'expecting one of: '
                "'false' 'true'"
            )

    @tatsumasu()
    def _rexp_(self):  # noqa
        self._aexp_()
        self.name_last_node('lhs')
        self._rop_()
        self.name_last_node('op')
        self._cut()
        self._aexp_()
        self.name_last_node('rhs')

        self._define(
            ['lhs', 'op', 'rhs'],
            []
        )

    @tatsumasu()
    def _rop_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('<=')
            with self._option():
                self._token('<')
            with self._option():
                self._token('=')
            with self._option():
                self._token('>=')
            with self._option():
                self._token('>')
            self._error(
                'expecting one of: '
                "'<' '<=' '=' '>' '>='"
            )

    @tatsumasu()
    def _aexp_(self):  # noqa
        with self._choice():
            with self._option():
                self._addition_()
            with self._option():
                self._subtraction_()
            with self._option():
                self._term_()
            self._error(
                'expecting one of: '
                '<addition> <division> <factor> <mult>'
                '<subtraction> <term>'
            )

    @tatsumasu()
    def _addition_(self):  # noqa
        self._term_()
        self.name_last_node('lhs')
        self._token('+')
        self.name_last_node('op')
        self._cut()
        self._aexp_()
        self.name_last_node('rhs')

        self._define(
            ['lhs', 'op', 'rhs'],
            []
        )

    @tatsumasu()
    def _subtraction_(self):  # noqa
        self._term_()
        self.name_last_node('lhs')
        self._token('-')
        self.name_last_node('op')
        self._cut()
        self._aexp_()
        self.name_last_node('rhs')

        self._define(
            ['lhs', 'op', 'rhs'],
            []
        )

    @tatsumasu()
    def _term_(self):  # noqa
        with self._choice():
            with self._option():
                self._mult_()
            with self._option():
                self._division_()
            with self._option():
                self._factor_()
            self._error(
                'expecting one of: '
                "'(' <atom> <division> <factor> <mult>"
                '<neg_number>'
            )

    @tatsumasu()
    def _mult_(self):  # noqa
        self._factor_()
        self.name_last_node('lhs')
        self._token('*')
        self.name_last_node('op')
        self._cut()
        self._term_()
        self.name_last_node('rhs')

        self._define(
            ['lhs', 'op', 'rhs'],
            []
        )

    @tatsumasu()
    def _division_(self):  # noqa
        self._factor_()
        self.name_last_node('lhs')
        self._token('/')
        self.name_last_node('op')
        self._cut()
        self._term_()
        self.name_last_node('rhs')

        self._define(
            ['lhs', 'op', 'rhs'],
            []
        )

    @tatsumasu()
    def _factor_(self):  # noqa
        with self._choice():
            with self._option():
                self._address_of_() # Added address of method
            with self._option():
                self._atom_()
            with self._option():
                self._neg_number_()
            with self._option():
                self._token('(')
                self._aexp_()
                self.name_last_node('@')
                self._token(')')
            self._error(
                'expecting one of: '
                "'(' '-' <atom> <name> <neg_number>"
                '<number> <address_of>'
            )
    # Extending pointer functionality with &
    @tatsumasu()
    def _address_of_(self):
        self._token('&')
        self._name_()
        self.name_last_node('var')
        self._define(
            ['var'],
            []
        )

    @tatsumasu()
    def _neg_number_(self):  # noqa
        self._token('-')
        self._cut()
        self._number_()
        self.name_last_node('@')

    @tatsumasu()
    def _atom_(self):  # noqa
        with self._choice():
            with self._option():
                self._name_()
            with self._option():
                self._number_()
            self._error(
                'expecting one of: '
                '<INT> <NAME> <name> <number>'
            )

    @tatsumasu()
    def _name_(self):  # noqa
        self._NAME_()

    @tatsumasu()
    def _number_(self):  # noqa
        self._INT_()

    @tatsumasu()
    def _INT_(self):  # noqa
        self._pattern('0[xX][0-9a-fA-F]+|[0-9]+')

    @tatsumasu()
    def _NAME_(self):  # noqa
        self._pattern('(?!\\d)\\w+')

    @tatsumasu()
    def _NEWLINE_(self):  # noqa
        self._pattern('[\\u000C\\r\\n]+')
        self._cut()


class WhileLangSemantics:
    def start(self, ast):  # noqa
        return ast

    def stmt_list(self, ast):  # noqa
        return ast

    def stmt(self, ast):  # noqa
        return ast

    def asgn_stmt(self, ast):  # noqa
        return ast

    def block_stmt(self, ast):  # noqa
        return ast

    def skip_stmt(self, ast):  # noqa
        return ast

    def print_state_stmt(self, ast):  # noqa
        return ast

    def print_heap_stmt(self, ast):  # noqa
        return ast

    def if_stmt(self, ast):  # noqa
        return ast

    def while_stmt(self, ast):  # noqa
        return ast

    def assert_stmt(self, ast):  # noqa
        return ast

    def assume_stmt(self, ast):  # noqa
        return ast

    def havoc_stmt(self, ast):  # noqa
        return ast

    def var_list(self, ast):  # noqa
        return ast

    def bexp(self, ast):  # noqa
        return ast

    def bterm(self, ast):  # noqa
        return ast

    def bfactor(self, ast):  # noqa
        return ast

    def batom(self, ast):  # noqa
        return ast

    def bool_const(self, ast):  # noqa
        return ast

    def rexp(self, ast):  # noqa
        return ast

    def rop(self, ast):  # noqa
        return ast

    def aexp(self, ast):  # noqa
        return ast

    def addition(self, ast):  # noqa
        return ast

    def subtraction(self, ast):  # noqa
        return ast

    def term(self, ast):  # noqa
        return ast

    def mult(self, ast):  # noqa
        return ast

    def division(self, ast):  # noqa
        return ast

    def factor(self, ast):  # noqa
        return ast

    def neg_number(self, ast):  # noqa
        return ast

    def atom(self, ast):  # noqa
        return ast

    def name(self, ast):  # noqa
        return ast

    def number(self, ast):  # noqa
        return ast

    def INT(self, ast):  # noqa
        return ast

    def NAME(self, ast):  # noqa
        return ast

    def NEWLINE(self, ast):  # noqa
        return ast


def main(filename, **kwargs):
    if not filename or filename == '-':
        text = sys.stdin.read()
    else:
        with open(filename) as f:
            text = f.read()
    parser = WhileLangParser()
    return parser.parse(
        text,
        filename=filename,
        **kwargs
    )


if __name__ == '__main__':
    import json
    from tatsu.util import asjson

    ast = generic_main(main, WhileLangParser, name='WhileLang')
    data = asjson(ast)
    print(json.dumps(data, indent=2))
