from pfn.lexer import Lexer
from pfn.parser import Parser


class TestParserExport:
    def test_parse_export_without_decorator(self):
        source = "def add(x, y) = x + y"
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        module = parser.parse()
        assert len(module.declarations) == 1
        decl = module.declarations[0]
        assert decl.name == "add"
        assert decl.is_exported is False
