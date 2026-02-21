from pfn.lexer import Lexer
from pfn.parser import Parser


class TestParserInterface:
    def test_parse_simple_interface(self):
        source = "interface Eq a where { eq : a -> a -> Bool }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert decl.name == "Eq"
        assert "a" in decl.params

    def test_parse_interface_with_multiple_methods(self):
        source = "interface Ord a where { compare : a -> a -> Ordering, lt : a -> a -> Bool }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        decl = module.declarations[0]
        assert len(decl.methods) == 2


class TestParserImpl:
    def test_parse_simple_impl(self):
        source = "impl Eq Int where { eq = (fn x => fn y => x == y) }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert decl.class_name == "Eq"

    def test_parse_impl_with_multiple_methods(self):
        source = "impl Show Int where { show = (fn x => toString(x)), shows = (fn x => toString(x)) }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        decl = module.declarations[0]
        assert len(decl.methods) == 2


class TestParserEffect:
    def test_parse_simple_effect(self):
        source = "effect IO { input : String, print : String }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert decl.name == "IO"
        assert len(decl.operations) == 2

    def test_parse_effect_with_state(self):
        source = "effect State s { get : s, put : s }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        decl = module.declarations[0]
        assert decl.name == "State"
        assert len(decl.operations) == 2
