# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest

from dependencies.grako.exceptions import FailedSemantics, FailedParse
from dependencies.grako.grammars import ModelContext
from dependencies.grako.parser import GrakoGrammarGenerator
from dependencies.grako.tool import genmodel
from dependencies.grako.util import trim, ustr, PY3
from dependencies.grako.codegen import codegen


class GrammarTests(unittest.TestCase):
    def test_keywords_in_rule_names(self):
        grammar = '''
            start
                =
                whitespace
                ;

            whitespace
                =
                    {'x'}+
                ;
        '''
        m = genmodel('Keywords', grammar)
        m.parse('x')

    def test_python_keywords_in_rule_names(self):
        # This is a regression test for
        # https://bitbucket.org/apalala/grako/issues/59
        # (semantic actions not called for rules with the same name as a python
        # keyword).
        grammar = '''
            not = 'x' ;
        '''
        m = genmodel('Keywords', grammar)

        class Semantics(object):
            def __init__(self):
                self.called = False

            def not_(self, ast):
                self.called = True

        semantics = Semantics()
        m.parse('x', semantics=semantics)
        assert semantics.called

    def test_update_ast(self):
        grammar = '''
            foo = name:"1" [ name: bar ] ;
            bar = { "2" } * ;
        '''
        m = genmodel('Keywords', grammar)
        ast = m.parse('1 2')
        self.assertEqual(['1', ['2']], ast.name)

        grammar = '''
            start = items: { item } * $ ;
            item = @:{ subitem } * "0" ;
            subitem = ?/1+/? ;
        '''
        m = genmodel('Update', grammar)
        ast = m.parse("1101110100", nameguard=False)
        self.assertEqual([['11'], ['111'], ['1'], []], ast.items_)

    def test_ast_assignment(self):
        grammar = '''
            n  = @: {"a"}* $ ;
            f  = @+: {"a"}* $ ;
            nn = @: {"a"}*  @: {"b"}* $ ;
            nf = @: {"a"}*  @+: {"b"}* $ ;
            fn = @+: {"a"}* @: {"b"}* $ ;
            ff = @+: {"a"}* @+: {"b"}* $ ;
        '''

        model = genmodel("test", grammar)

        def p(input, rule):
            return model.parse(input, start=rule, whitespace='')

        e = self.assertEqual

        e([], p('', 'n'))
        e(['a'], p('a', 'n'))
        e(['a', 'a'], p('aa', 'n'))

        e([[]], p('', 'f'))
        e([['a']], p('a', 'f'))
        e([['a', 'a']], p('aa', 'f'))

        for r in ('nn', 'nf', 'fn', 'ff'):
            e([[], []], p('', r))
            e([['a'], []], p('a', r))
            e([[], ['b']], p('b', r))
            e([['a', 'a'], []], p('aa', r))
            e([[], ['b', 'b']], p('bb', r))
            e([['a', 'a'], ['b']], p('aab', r))

    def test_stateful(self):
        # Parser for mediawiki-style unordered lists.
        grammar = r'''
        document = @:ul [ nl ] $ ;
        ul = "*" ul_start el+:li { nl el:li } * ul_end ;
        li = ul | li_text ;
        (* Quirk: If a text line is followed by a sublist, the sublist does not get its own li. *)
        li_text = text:text [ ul:li_followed_by_ul ] ;
        li_followed_by_ul = nl @:ul ;
        text = ?/.*/? ;
        nl = ?/\n/? ul_marker ;
        (* The following rules are placeholders for state transitions. *)
        ul_start = () ;
        ul_end = () ;
        (* The following rules are placeholders for state validations and grammar rules. *)
        ul_marker = () ;
        '''

        class StatefulSemantics(object):
            def __init__(self, parser):
                self._context = parser

            def ul_start(self, ast):
                ctx = self._context
                ctx._state = 1 if ctx._state is None else ctx._state + 1
                return ast

            def ul_end(self, ast):
                ctx = self._context
                ctx._state = None if ctx._state is None or ctx._state <= 1 else ctx._state - 1
                return ast

            def ul_marker(self, ast):
                ctx = self._context
                if ctx._state is not None:
                    if not ctx.buf.match("*" * ctx._state):
                        raise FailedSemantics("not at correct level")
                return ast

            def ul(self, ast):
                return "<ul>" + "".join(ast.el) + "</ul>"

            def li(self, ast):
                return "<li>" + ast + "</li>"

            def li_text(self, ast):
                return ast.text if ast.ul is None else ast.text + ast.ul

        model = genmodel("test", grammar)
        context = ModelContext(model.rules, whitespace='', nameguard=False)
        ast = model.parse('*abc', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li></ul>")
        ast = model.parse('*abc\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual("<ul><li>abc</li></ul>", ast)
        ast = model.parse('*abc\n*def\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual("<ul><li>abc</li><li>def</li></ul>", ast)
        ast = model.parse('**abc', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual("<ul><li><ul><li>abc</li></ul></li></ul>", ast)
        ast = model.parse('*abc\n**def\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual("<ul><li>abc<ul><li>def</li></ul></li></ul>", ast)

    def test_optional_closure(self):
        grammar = 'start = foo+:"x" foo:{"y"}* {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" [foo+:{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" foo:[{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

        grammar = 'start = foo+:"x" [foo:{"y"}*] {foo:"z"}* ;'
        model = genmodel("test", grammar)
        ast = model.parse("xyyzz", nameguard=False)
        self.assertEqual(['x', ['y', 'y'], 'z', 'z'], ast.foo)

    def test_optional_sequence(self):
        grammar = '''
            start = '1' ['2' '3'] '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEqual(['1', '2', '3', '4'], ast)

        grammar = '''
            start = '1' foo:['2' '3'] '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEqual(['2', '3'], ast.foo)

    def test_group_ast(self):
        grammar = '''
            start = '1' ('2' '3') '4' $ ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1234", nameguard=False)
        self.assertEqual(['1', '2', '3', '4'], ast)

    def test_partial_options(self):
        grammar = '''
            start
                =
                [a]
                [
                    'A' 'A'
                |
                    'A' 'B'
                ]
                $
                ;
            a
                =
                'A' !('A'|'B')
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("AB", nameguard=False)
        self.assertEqual(['A', 'B'], ast)

    def test_partial_choice(self):
        grammar = '''
            start
                =
                o:[o]
                x:'A'
                $
                ;
            o
                =
                'A' a:'A'
                |
                'A' b:'B'
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("A", nameguard=False)
        self.assertEqual({'x': 'A', 'o': None}, ast)

    def test_patterns_with_newlines(self):
        grammar = '''
            start
                =
                blanklines $
                ;

            blanklines
                =
                blankline [blanklines]
                ;

            blankline
                =
                /^[^\n]*\n?$/
                ;

            blankline2 =
                ?/^[^\n]*\n?$/?
                ;
        '''

        model = genmodel("test", grammar)
        ast = model.parse('\n\n')
        self.assertEqual('', ustr(ast))

    def test_new_override(self):
        grammar = '''
            start
                =
                @:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEqual(['a', 'b', 'b'], ast)

    def test_list_override(self):
        grammar = '''
            start
                =
                @+:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEqual(['a'], ast)

        grammar = '''
            start
                =
                @:'a' {@:'b'}
                $
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("a", nameguard=False)
        self.assertEqual('a', ast)

    def test_based_rule(self):
        grammar = '''\
            start
                =
                b $
                ;


            a
                =
                @:'a'
                ;


            b < a
                =
                {@:'b'}
                ;
            '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEqual(['a', 'b', 'b'], ast)
        self.assertEqual(trim(grammar), ustr(model))

    def test_rule_include(self):
        grammar = '''
            start = b $;

            a = @:'a' ;
            b = >a {@:'b'} ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEqual(['a', 'b', 'b'], ast)

    def test_direct_left_recursion(self):
        grammar = '''
            start
                =
                expre $
                ;

            expre
                =
                expre '+' number
                |
                expre '*' number
                |
                number
                ;

            number
                =
                ?/[0-9]+/?
                ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("1*2+3*5")
        self.assertEqual(['1', '*', '2', '+', '3', '*', '5'], ast)

    def test_indirect_left_recursion(self):
        grammar = '''
        start = x $ ;
        x = expr ;
        expr = x '-' num | num;
        num = ?/[0-9]+/? ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("5-87-32")
        self.assertEqual(['5', '-', '87', '-', '32'], ast)

    def test_indirect_left_recursion_with_cut(self):
        grammar = '''
        start = x $ ;
        x = expr ;
        expr = x '-' ~ num | num;
        num = ?/[0-9]+/? ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("5-87-32")
        self.assertEqual(['5', '-', '87', '-', '32'], ast)

    def test_indirect_left_recursion_complex(self):
        grammar = '''
        start = Primary $ ;
        Primary = PrimaryNoNewArray ;

        PrimaryNoNewArray =
          ClassInstanceCreationExpression
        | MethodInvocation
        | FieldAccess
        | ArrayAccess
        | 'this' ;

        ClassInstanceCreationExpression =
          'new' ClassOrInterfaceType '(' ')'
        | Primary '.new' Identifier '()' ;

        MethodInvocation =
          Primary '.' MethodName '()'
        | MethodName '()' ;

        FieldAccess =
          Primary '.' Identifier
        | 'super.' Identifier ;

        ArrayAccess =
          Primary '[' Expression ']'
        | ExpressionName '[' Expression ']' ;

        ClassOrInterfaceType =
          ClassName
        | InterfaceTypeName ;

        ClassName = 'C' | 'D' ;
        InterfaceTypeName = 'I' | 'J' ;
        Identifier = 'x' | 'y' | ClassOrInterfaceType ;
        MethodName = 'm' | 'n' ;
        ExpressionName = Identifier ;
        Expression = 'i' | 'j' ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("this")
        self.assertEqual('this', ast)
        ast = model.parse("this.x")
        self.assertEqual(['this', '.', 'x'], ast)
        ast = model.parse("this.x.y")
        self.assertEqual(['this', '.', 'x', '.', 'y'], ast)
        ast = model.parse("this.x.m()")
        self.assertEqual(['this', '.', 'x', '.', 'm', '()'], ast)
        ast = model.parse("x[i][j].y")
        self.assertEqual(['x', '[', 'i', ']', '[', 'j', ']', '.', 'y'], ast)

    def test_no_left_recursion(self):
        grammar = '''
            start
                =
                expre $
                ;

            expre
                =
                expre '+' number
                |
                expre '*' number
                |
                number
                ;

            number
                =
                ?/[0-9]+/?
                ;
        '''
        model = genmodel("test", grammar)
        model.parse("1*2+3*5")
        try:
            model.parse("1*2+3*5", left_recursion=False)
            self.fail('expected left recursion failure')
        except FailedParse:
            pass

    def test_nested_left_recursion(self):
        grammar_a = '''
        s = e $ ;
        e = [e '+'] t ;
        t = [t '*'] a ;
        a = ?/[0-9]/? ;
        '''
        grammar_b = '''
        s = e $ ;
        e = [e '+'] a ;
        a = n | p ;
        n = ?/[0-9]/? ;
        p = '(' @:e ')' ;
        '''
        model_a = genmodel("test", grammar_a)
        model_b = genmodel("test", grammar_b)
        ast = model_a.parse("1*2+3*4")
        self.assertEqual(['1', '*', '2', '+', ['3', '*', '4']], ast)
        ast = model_b.parse("(1+2)+(3+4)")
        self.assertEqual(['1', '+', '2', '+', ['3', '+', '4']], ast)
        ast = model_a.parse("1*2*3")
        self.assertEqual(['1', '*', '2', '*', '3'], ast)
        ast = model_b.parse("(((1+2)))")
        self.assertEqual(['1', '+', '2'], ast)

    def test_keyword_params(self):
        grammar = '''
            start(k1=1, k2=2)
                =
                {'a'} $
                ;
        '''
        g = GrakoGrammarGenerator('Keywords')
        model = g.parse(grammar, trace=False)
        code = codegen(model)
        self.assertEqual('#!/usr/bin/env python', code.splitlines()[0])
        pass

    def test_35_only_keyword_params(self):
        grammar = '''
            rule(kwdA=A, kwdB=B)
                =
                'a'
                ;
        '''
        model = genmodel("test", grammar)
        self.assertEqual(trim(grammar), ustr(model))

    def test_36_params_and_keyword_params(self):
        grammar = '''
            rule(A, kwdB=B)
                =
                'a'
                ;
        '''
        model = genmodel("test", grammar)
        self.assertEqual(trim(grammar), ustr(model))

    def test_36_param_combinations(self):
        def assert_equal(target, value):
            self.assertEqual(target, value)

        class TC36Semantics(object):

            """Check all rule parameters for expected types and values"""

            def rule_positional(self, ast, p1, p2, p3, p4):
                assert_equal("ABC", p1)
                assert_equal(123, p2)
                assert_equal('=', p3)
                assert_equal("+", p4)
                return ast

            def rule_keyword(self, ast, k1, k2, k3, k4):
                assert_equal("ABC", k1)
                assert_equal(123, k2)
                assert_equal('=', k3)
                assert_equal('+', k4)
                return ast

            def rule_all(self, ast, p1, p2, p3, p4, k1, k2, k3, k4):
                assert_equal("DEF", p1)
                assert_equal(456, p2)
                assert_equal('=', p3)
                assert_equal("+", p4)
                assert_equal("HIJ", k1)
                assert_equal(789, k2)
                assert_equal('=', k3)
                assert_equal('+', k4)
                return ast

        grammar = '''
            start
                =
                {rule_positional | rule_keywords | rule_all} $
                ;


            rule_positional('ABC', 123, '=', '+')
                =
                'a'
                ;


            rule_keywords(k1=ABC, k3='=', k4='+', k2=123)
                =
                'b'
                ;


            rule_all('DEF', 456, '=', '+', k1=HIJ, k3='=', k4='+', k2=789)
                =
                'c'
                ;
        '''

        pretty = '''
            start
                =
                {rule_positional | rule_keywords | rule_all} $
                ;


            rule_positional(ABC, 123, '=', '+')
                =
                'a'
                ;


            rule_keywords(k1=ABC, k3='=', k4='+', k2=123)
                =
                'b'
                ;


            rule_all(DEF, 456, '=', '+', k1=HIJ, k3='=', k4='+', k2=789)
                =
                'c'
                ;
        '''

        model = genmodel('RuleArguments', grammar)
        self.assertEqual(trim(pretty), ustr(model))
        model = genmodel('RuleArguments', pretty)

        ast = model.parse("a b c")
        self.assertEqual(['a', 'b', 'c'], ast)
        semantics = TC36Semantics()
        ast = model.parse("a b c", semantics=semantics)
        self.assertEqual(['a', 'b', 'c'], ast)
        codegen(model)

    def test_36_unichars(self):
        grammar = '''
            start = { rule_positional | rule_keywords | rule_all }* $ ;

            rule_positional("ÄÖÜäöüß") = 'a' ;

            rule_keywords(k1='äöüÄÖÜß') = 'b' ;

            rule_all('ßÄÖÜäöü', k1="ßäöüÄÖÜ") = 'c' ;
        '''

        def _trydelete(pymodule):
            import os
            try:
                os.unlink(pymodule + ".py")
            except EnvironmentError:
                pass
            try:
                os.unlink(pymodule + ".pyc")
            except EnvironmentError:
                pass
            try:
                os.unlink(pymodule + ".pyo")
            except EnvironmentError:
                pass

        def assert_equal(target, value):
            self.assertEqual(target, value)

        class UnicharsSemantics(object):
            """Check all rule parameters for expected types and values"""
            def rule_positional(self, ast, p1):
                assert_equal("ÄÖÜäöüß", p1)
                return ast

            def rule_keyword(self, ast, k1):
                assert_equal("äöüÄÖÜß", k1)
                return ast

            def rule_all(self, ast, p1, k1):
                assert_equal("ßÄÖÜäöü", p1)
                assert_equal("ßäöüÄÖÜ", k1)
                return ast

        m = genmodel("UnicodeRuleArguments", grammar)
        ast = m.parse("a b c")
        self.assertEqual(['a', 'b', 'c'], ast)

        semantics = UnicharsSemantics()
        ast = m.parse("a b c", semantics=semantics)
        self.assertEqual(['a', 'b', 'c'], ast)

        code = codegen(m)
        import codecs
        with codecs.open("tc36unicharstest.py", "w", "utf-8") as f:
            f.write(code)
        import tc36unicharstest
        tc36unicharstest
        _trydelete("tc36unicharstest")

    def test_numbers_and_unicode(self):
        grammar = '''
            rúle(1, -23, 4.56, 7.89e-11, 0xABCDEF, Añez)
                =
                'a'
                ;
        '''
        rule2 = '''

            rulé(Añez)
                =
                '\\xf1'
                ;
        '''
        rule3 = '''

            rúlé(Añez)
                =
                'ñ'
                ;
        '''
        if PY3:
            grammar += rule3
        else:
            grammar += rule2

        model = genmodel("test", grammar)
        self.assertEqual(trim(grammar), ustr(model))

    def test_48_rule_override(self):
        grammar = '''
            start = ab $;

            ab = 'xyz' ;

            @override
            ab = @:'a' {@:'b'} ;
        '''
        model = genmodel("test", grammar)
        ast = model.parse("abb", nameguard=False)
        self.assertEqual(['a', 'b', 'b'], ast)

    def test_whitespace_directive(self):
        grammar = '''
            @@whitespace :: /[\t ]+/

            test = "test" $;
        '''
        model = genmodel("test", grammar)
        code = codegen(model)
        compile(code, 'test.py', 'exec')

    def test_eol_comments_re_directive(self):
        grammar = '''
            @@eol_comments :: /#.*?$/

            test = "test" $;
        '''
        model = genmodel("test", grammar)
        code = codegen(model)
        compile(code, 'test.py', 'exec')

    def test_left_recursion_directive(self):
        grammar = '''
            @@left_recursion :: False

            test = "test" $;
        '''
        model = genmodel("test", grammar)
        self.assertFalse(model.directives.get('left_recursion'))
        self.assertFalse(model.left_recursion)

        code = codegen(model)
        compile(code, 'test.py', 'exec')

    def test_failed_ref(self):
        grammar = """
            final = object;
            type = /[^\s=()]+/;
            object = '('type')' '{' @:{pair} {',' @:{pair}}* [','] '}';
            pair = key '=' value;
            list = '('type')' '[' @:{object} {',' @:{object}}* [','] ']';
            key = /[^\s=]+/;
            value = @:(string|list|object|unset|boolean|number|null) [','];
            null = '('type')' @:{ 'null' };
            boolean = /(true|false)/;
            unset = '<unset>';
            string = '"' @:/[^"]*/ '"';
            number = /-?[0-9]+/;
        """

        model = genmodel("final", grammar)
        codegen(model)
        model.parse('(sometype){boolean = true}')

    def test_whitespace_no_newlines(self):
        grammar = """
            @@whitespace :: /[\t ]+/
            # this is just a token with any character but space and newline
            # it should finish before it capture space or newline character
            token = /[^ \n]+/;
            # expect whitespace to capture spaces between tokens, but newline should be captured afterwards
            token2 = {token}* /\n/;
            # document is just list of this strings of tokens
            document = {@+:token2}* $;
        """
        text = trim("""\
            a b
            c d
            e f
        """)

        expected = [
            [
                [
                    "a",
                    "b"
                ],
                "\n"
            ],
            [
                [
                    "c",
                    "d"
                ],
                "\n"
            ],
            [
                [
                    "e",
                    "f"
                ],
                "\n"
            ]
        ]

        model = genmodel("document", grammar)
        ast = model.parse(text, start='document')
        self.assertEqual(expected, ast)

    def test_empty_match_token(self):
        grammar = """
            table = { row }+ ;
            row = (cell1:cell "|" cell2:cell) "\n";
            cell = /[a-z]+/ ;
        """
        try:
            genmodel("model", grammar)
            self.fail('allowed empty token')
        except FailedParse:
            pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(GrammarTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()
