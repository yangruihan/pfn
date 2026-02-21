from pfn.lexer import Lexer
from pfn.parser import Parser


class TestGADTParsing:
    def test_parse_simple_gadt(self):
        source = "gadt Expr a where { Lit, Var }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert decl.name == "Expr"
        assert decl.is_gadt is True
        assert len(decl.constructors) == 2

    def test_gadt_with_single_constructor(self):
        source = "gadt Maybe a where { Nothing }"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        decl = module.declarations[0]
        assert decl.is_gadt is True
        assert len(decl.constructors) == 1
        assert decl.constructors[0].name == "Nothing"
