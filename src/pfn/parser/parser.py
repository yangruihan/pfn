from __future__ import annotations

from pfn.lexer import Token, TokenType
from pfn.parser import ast
from pfn.types import TFun


class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at {token.span}")


class Parser:
    PRECEDENCE: dict[TokenType, int] = {
        TokenType.DOUBLE_PIPE: 1,
        TokenType.DOUBLE_AMP: 2,
        TokenType.EQ: 3,
        TokenType.NEQ: 3,
        TokenType.LT: 3,
        TokenType.LE: 3,
        TokenType.GT: 3,
        TokenType.GE: 3,
        TokenType.DOUBLE_COLON: 4,
        TokenType.DOUBLE_PLUS: 5,
        TokenType.PLUS: 6,
        TokenType.MINUS: 6,
        TokenType.STAR: 7,
        TokenType.SLASH: 7,
        TokenType.PERCENT: 7,
        TokenType.FAT_ARROW: 8,
    }

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ast.Module:
        declarations = []
        while not self._check(TokenType.EOF):
            decl = self._parse_declaration()
            if decl is not None:
                declarations.append(decl)
        return ast.Module(declarations=declarations)

    def parse_expr(self) -> ast.Expr:
        return self._parse_expr()

    def _current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def _check(self, *types: TokenType) -> bool:
        return self._current().type in types

    def _match(self, *types: TokenType) -> Token | None:
        if self._check(*types):
            token = self._current()
            self.pos += 1
            return token
        return None

    def _expect(self, type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._match(type)
        raise ParseError(message, self._current())

    def _parse_declaration(self) -> ast.Decl | None:
        if self._match(TokenType.KW_DEF):
            return self._parse_def()
        if self._match(TokenType.AT):
            if self._check(TokenType.IDENT) and str(self._current().value) == "py":
                self.pos += 1
                if self._match(TokenType.DOT):
                    if (
                        self._check(TokenType.IDENT)
                        and str(self._current().value) == "export"
                    ):
                        self.pos += 1
                        export_name = None
                        if self._match(TokenType.LPAREN):
                            name_token = self._expect(
                                TokenType.STRING, "Expected export name"
                            )
                            export_name = (
                                str(name_token.value) if name_token.value else None
                            )
                            self._expect(TokenType.RPAREN, "Expected ')'")
                        self._expect(
                            TokenType.KW_DEF, "Expected 'def' after @py.export"
                        )
                        def_decl = self._parse_def()
                        def_decl.is_exported = True
                        def_decl.export_name = export_name
                        return def_decl
            self.pos -= 1
        if self._match(TokenType.KW_TYPE):
            return self._parse_type()
        if self._match(TokenType.KW_GADT):
            return self._parse_gadt()
        if self._match(TokenType.KW_IMPORT):
            return self._parse_import()
        if self._match(TokenType.KW_INTERFACE):
            return self._parse_interface()
        if self._match(TokenType.KW_IMPL):
            return self._parse_impl()
        if self._match(TokenType.KW_EFFECT):
            return self._parse_effect()
        raise ParseError(f"Unexpected token: {self._current().type}", self._current())

    def _parse_def(self) -> ast.DefDecl:
        is_exported = False
        export_name = None

        if self._match(TokenType.AT):
            if self._check(TokenType.IDENT) and str(self._current().value) == "py":
                self.pos += 1
                if self._match(TokenType.DOT):
                    if (
                        self._check(TokenType.IDENT)
                        and str(self._current().value) == "export"
                    ):
                        self.pos += 1
                        is_exported = True
                        if self._match(TokenType.LPAREN):
                            name_token = self._expect(
                                TokenType.STRING, "Expected export name"
                            )
                            export_name = (
                                str(name_token.value) if name_token.value else None
                            )
                            self._expect(TokenType.RPAREN, "Expected ')'")

        name_token = self._expect(TokenType.IDENT, "Expected function name")
        name = name_token.value

        params = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                params.append(self._parse_param())
                while self._match(TokenType.COMMA):
                    params.append(self._parse_param())
            self._expect(TokenType.RPAREN, "Expected ')' after parameters")

        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._parse_type_ref()

        self._expect(TokenType.EQUALS, "Expected '=' after function signature")
        body = self._parse_expr()

        return ast.DefDecl(
            name=name,
            params=params,
            return_type=return_type,
            body=body,
            is_exported=is_exported,
            export_name=export_name,
        )

    def _parse_param(self) -> ast.Param:
        name_token = self._expect(TokenType.IDENT, "Expected parameter name")
        name = name_token.value
        type_annotation = None
        if self._match(TokenType.COLON):
            type_annotation = self._parse_type_ref()
        return ast.Param(name=name, type_annotation=type_annotation)

    def _parse_type(self) -> ast.TypeDecl:
        name_token = self._expect(TokenType.IDENT, "Expected type name")
        name = name_token.value

        params = []
        while self._check(TokenType.IDENT):
            peek_type = self._peek().type
            if peek_type in (TokenType.EQUALS, TokenType.PIPE, TokenType.EOF):
                param_token = self._match(TokenType.IDENT)
                if param_token:
                    params.append(param_token.value)
            else:
                break

        if self._match(TokenType.EQUALS):
            type_ref = self._parse_type_ref()
            if isinstance(type_ref, ast.RecordTypeRef):
                return ast.TypeDecl(
                    name=name,
                    params=params,
                    is_record=True,
                    record_fields=type_ref.fields,
                )

        constructors = []
        while self._match(TokenType.PIPE):
            ctor_name_token = self._expect(TokenType.IDENT, "Expected constructor name")
            ctor_name = ctor_name_token.value
            ctor_fields = []
            while self._check(TokenType.IDENT) and not self._check(
                TokenType.PIPE, TokenType.EOF
            ):
                field_type = self._parse_type_atom()
                ctor_fields.append(field_type)
            constructors.append(ast.Constructor(name=ctor_name, fields=ctor_fields))

        return ast.TypeDecl(name=name, params=params, constructors=constructors)

    def _parse_gadt(self) -> ast.TypeDecl:
        name_token = self._expect(TokenType.IDENT, "Expected type name")
        name = str(name_token.value)

        params = []
        while self._check(TokenType.IDENT):
            params.append(str(self._current().value))
            self.pos += 1

        self._expect(TokenType.KW_WHERE, "Expected 'where'")
        self._expect(TokenType.LBRACE, "Expected '{'")

        constructors = []
        while not self._check(TokenType.RBRACE):
            ctor_name_token = self._expect(TokenType.IDENT, "Expected constructor name")
            ctor_name = str(ctor_name_token.value)

            ctor_params = []
            while self._check(TokenType.IDENT):
                param_type = self._parse_type_ref()
                ctor_params.append(param_type)

            constructors.append(ast.Constructor(name=ctor_name, fields=ctor_params))
            if not self._match(TokenType.COMMA):
                break

        self._expect(TokenType.RBRACE, "Expected '}'")

        type_decl = ast.TypeDecl(name=name, params=params, constructors=constructors)
        type_decl.is_gadt = True
        return type_decl

    def _peek(self) -> Token:
        if self.pos + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + 1]

    def _parse_import(self) -> ast.ImportDecl:
        is_python = False

        if self._check(TokenType.IDENT) and str(self._current().value) == "python":
            is_python = True
            self.pos += 1

        if self._match(TokenType.IDENT):
            module_parts = [self.tokens[self.pos - 1].value]
            while self._match(TokenType.DOT):
                part = self._expect(TokenType.IDENT, "Expected module part")
                module_parts.append(part.value)
            module_name = ".".join([str(p) for p in module_parts])
        else:
            raise ParseError("Expected module name", self._current())

        alias = None
        exposing = None

        if self._match(TokenType.KW_AS):
            alias_token = self._expect(TokenType.IDENT, "Expected alias")
            alias = str(alias_token.value)

        return ast.ImportDecl(
            module=module_name, alias=alias, exposing=exposing, is_python=is_python
        )

    def _parse_type_ref(self) -> ast.TypeRef:
        return self._parse_type_arrow()

    def _parse_type_arrow(self) -> ast.TypeRef:
        left = self._parse_type_app()
        if self._match(TokenType.ARROW):
            right = self._parse_type_arrow()
            return ast.FunTypeRef(param=left, result=right)
        return left

    def _parse_type_app(self) -> ast.TypeRef:
        base = self._parse_type_atom()
        args = []
        while self._check(TokenType.IDENT):
            args.append(self._parse_type_atom())
        if args:
            if isinstance(base, ast.SimpleTypeRef):
                return ast.SimpleTypeRef(name=base.name, args=args)
        return base

    def _parse_type_atom(self) -> ast.TypeRef:
        if self._match(TokenType.LPAREN):
            inner = self._parse_type_ref()
            if self._match(TokenType.COMMA):
                elements = [inner]
                while not self._check(TokenType.RPAREN):
                    elements.append(self._parse_type_ref())
                    if not self._match(TokenType.COMMA):
                        break
                self._expect(TokenType.RPAREN, "Expected ')' after tuple type")
                return ast.TupleTypeRef(elements=elements)
            self._expect(TokenType.RPAREN, "Expected ')'")
            return inner

        if self._match(TokenType.LBRACKET):
            element_type = self._parse_type_ref()
            self._expect(TokenType.RBRACKET, "Expected ']' after list type")
            return ast.SimpleTypeRef(name="List", args=[element_type])

        if self._match(TokenType.LBRACE):
            fields = []
            if not self._check(TokenType.RBRACE):
                while True:
                    field_name = self._expect(TokenType.IDENT, "Expected field name")
                    self._expect(TokenType.COLON, "Expected ':' after field name")
                    field_type = self._parse_type_ref()
                    fields.append((field_name.value, field_type))
                    if not self._match(TokenType.COMMA):
                        break
            self._expect(TokenType.RBRACE, "Expected '}' after record type")
            return ast.RecordTypeRef(fields=fields)

        name_token = self._expect(TokenType.IDENT, "Expected type name")
        return ast.SimpleTypeRef(name=name_token.value)

    def _parse_expr(self) -> ast.Expr:
        return self._parse_let()

    def _parse_let(self) -> ast.Expr:
        if self._match(TokenType.KW_LET):
            name_token = self._expect(TokenType.IDENT, "Expected variable name")
            name = name_token.value

            params = []
            while self._check(TokenType.IDENT, TokenType.LPAREN):
                if self._match(TokenType.LPAREN):
                    params.append(self._parse_param())
                    self._expect(TokenType.RPAREN, "Expected ')'")
                else:
                    params.append(self._parse_param())

            self._expect(TokenType.EQUALS, "Expected '=' after let binding")
            value = self._parse_expr()

            self._match(TokenType.KW_IN)
            body = self._parse_expr()

            if params:
                return ast.LetFunc(name=name, params=params, value=value, body=body)
            return ast.Let(name=name, value=value, body=body)

        if self._match(TokenType.KW_DO):
            return self._parse_do()

        return self._parse_if()

    def _parse_do(self) -> ast.DoNotation:
        bindings = []
        while not self._check(TokenType.KW_IN):
            name_token = self._expect(
                TokenType.IDENT, "Expected variable name in do binding"
            )
            name = name_token.value
            self._match(TokenType.LEFT_ARROW)
            value = self._parse_expr()
            bindings.append(ast.DoBinding(name=name, value=value))

        self._match(TokenType.KW_IN)
        body = self._parse_expr()

        return ast.DoNotation(bindings=bindings, body=body)

    def _parse_if(self) -> ast.Expr:
        if self._match(TokenType.KW_IF):
            cond = self._parse_expr()
            self._expect(TokenType.KW_THEN, "Expected 'then'")
            then_branch = self._parse_expr()
            self._expect(TokenType.KW_ELSE, "Expected 'else'")
            else_branch = self._parse_expr()
            return ast.If(cond=cond, then_branch=then_branch, else_branch=else_branch)
        return self._parse_match()

    def _parse_match(self) -> ast.Expr:
        if self._match(TokenType.KW_MATCH):
            scrutinee = self._parse_expr()
            self._expect(TokenType.KW_WITH, "Expected 'with'")
            cases = []
            while self._match(TokenType.PIPE):
                pattern = self._parse_pattern()
                guard = None
                if self._match(TokenType.KW_IF):
                    guard = self._parse_expr()
                self._expect(TokenType.ARROW, "Expected '->'")
                body = self._parse_expr()
                cases.append(ast.MatchCase(pattern=pattern, guard=guard, body=body))
            return ast.Match(scrutinee=scrutinee, cases=cases)
        return self._parse_or()

    def _parse_pattern(self) -> ast.Pattern:
        return self._parse_cons_pattern()

    def _parse_cons_pattern(self) -> ast.Pattern:
        left = self._parse_atom_pattern()
        if self._match(TokenType.DOUBLE_COLON):
            right = self._parse_cons_pattern()
            return ast.ConsPattern(head=left, tail=right)
        return left

    def _parse_atom_pattern(self) -> ast.Pattern:
        if self._match(TokenType.INT):
            return ast.IntPattern(value=self.tokens[self.pos - 1].value)
        if self._match(TokenType.FLOAT):
            return ast.FloatPattern(value=self.tokens[self.pos - 1].value)
        if self._match(TokenType.STRING):
            return ast.StringPattern(value=self.tokens[self.pos - 1].value)
        if self._match(TokenType.CHAR):
            return ast.CharPattern(value=self.tokens[self.pos - 1].value)
        if self._match(TokenType.TRUE):
            return ast.BoolPattern(value=True)
        if self._match(TokenType.FALSE):
            return ast.BoolPattern(value=False)
        if self._match(TokenType.UNDERSCORE):
            return ast.WildcardPattern()
        if self._match(TokenType.LBRACKET):
            if self._match(TokenType.RBRACKET):
                return ast.ListPattern(elements=[])
            elements = [self._parse_pattern()]
            while self._match(TokenType.COMMA):
                elements.append(self._parse_pattern())
            self._expect(TokenType.RBRACKET, "Expected ']'")
            return ast.ListPattern(elements=elements)
        if self._match(TokenType.LPAREN):
            if self._match(TokenType.RPAREN):
                return ast.TuplePattern(elements=[])
            first = self._parse_pattern()
            if self._match(TokenType.COMMA):
                elements = [first]
                while not self._check(TokenType.RPAREN):
                    elements.append(self._parse_pattern())
                    if not self._match(TokenType.COMMA):
                        break
                self._expect(TokenType.RPAREN, "Expected ')'")
                return ast.TuplePattern(elements=elements)
            self._expect(TokenType.RPAREN, "Expected ')'")
            return first
        if self._match(TokenType.IDENT):
            name = self.tokens[self.pos - 1].value
            return ast.VarPattern(name=name)

        raise ParseError(
            f"Expected pattern, got {self._current().type}", self._current()
        )

    def _parse_or(self) -> ast.Expr:
        left = self._parse_and()
        while self._match(TokenType.DOUBLE_PIPE):
            right = self._parse_and()
            left = ast.BinOp(left=left, op="||", right=right)
        return left

    def _parse_and(self) -> ast.Expr:
        left = self._parse_comparison()
        while self._match(TokenType.DOUBLE_AMP):
            right = self._parse_comparison()
            left = ast.BinOp(left=left, op="&&", right=right)
        return left

    def _parse_comparison(self) -> ast.Expr:
        left = self._parse_cons()
        while self._match(
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.LE,
            TokenType.GT,
            TokenType.GE,
        ):
            op = self.tokens[self.pos - 1].value
            right = self._parse_cons()
            left = ast.BinOp(left=left, op=op, right=right)
        return left

    def _parse_cons(self) -> ast.Expr:
        left = self._parse_concat()
        if self._match(TokenType.DOUBLE_COLON):
            right = self._parse_cons()
            return ast.BinOp(left=left, op="::", right=right)
        return left

    def _parse_concat(self) -> ast.Expr:
        left = self._parse_additive()
        while self._match(TokenType.DOUBLE_PLUS):
            right = self._parse_additive()
            left = ast.BinOp(left=left, op="++", right=right)
        return left

    def _parse_additive(self) -> ast.Expr:
        left = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self.tokens[self.pos - 1].value
            right = self._parse_multiplicative()
            left = ast.BinOp(left=left, op=op, right=right)
        return left

    def _parse_multiplicative(self) -> ast.Expr:
        left = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.tokens[self.pos - 1].value
            right = self._parse_unary()
            left = ast.BinOp(left=left, op=op, right=right)
        return left

    def _parse_unary(self) -> ast.Expr:
        if self._match(TokenType.MINUS, TokenType.BANG):
            op = self.tokens[self.pos - 1].value
            operand = self._parse_unary()
            return ast.UnaryOp(op=op, operand=operand)
        return self._parse_application()

    def _parse_application(self) -> ast.Expr:
        expr = self._parse_access()

        while True:
            if self._match(TokenType.LPAREN):
                args = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._parse_expr())
                    while self._match(TokenType.COMMA):
                        args.append(self._parse_expr())
                self._expect(TokenType.RPAREN, "Expected ')'")
                for arg in args:
                    expr = ast.App(func=expr, args=[arg])
            else:
                break

        return expr

    def _parse_access(self) -> ast.Expr:
        expr = self._parse_atom()

        while True:
            if self._match(TokenType.DOT):
                field_token = self._expect(TokenType.IDENT, "Expected field name")
                expr = ast.FieldAccess(expr=expr, field=field_token.value)
            elif self._match(TokenType.LBRACKET):
                index = self._parse_expr()
                self._expect(TokenType.RBRACKET, "Expected ']'")
                expr = ast.IndexAccess(expr=expr, index=index)
            else:
                break

        return expr

    def _parse_atom(self) -> ast.Expr:
        if self._match(TokenType.INT):
            return ast.IntLit(value=self.tokens[self.pos - 1].value)

        if self._match(TokenType.FLOAT):
            return ast.FloatLit(value=self.tokens[self.pos - 1].value)

        if self._match(TokenType.STRING):
            return ast.StringLit(value=self.tokens[self.pos - 1].value)

        if self._match(TokenType.CHAR):
            return ast.CharLit(value=self.tokens[self.pos - 1].value)

        if self._match(TokenType.TRUE):
            return ast.BoolLit(value=True)

        if self._match(TokenType.FALSE):
            return ast.BoolLit(value=False)

        if self._match(TokenType.KW_FN):
            return self._parse_lambda()

        if self._match(TokenType.LPAREN):
            if self._match(TokenType.RPAREN):
                return ast.UnitLit()

            first = self._parse_expr()

            if self._match(TokenType.COMMA):
                elements = [first]
                while not self._check(TokenType.RPAREN):
                    elements.append(self._parse_expr())
                    if not self._match(TokenType.COMMA):
                        break
                self._expect(TokenType.RPAREN, "Expected ')'")
                return ast.TupleLit(elements=elements)

            self._expect(TokenType.RPAREN, "Expected ')'")
            return first

        if self._match(TokenType.LBRACKET):
            if self._match(TokenType.RBRACKET):
                return ast.ListLit(elements=[])

            elements = [self._parse_expr()]
            while self._match(TokenType.COMMA):
                elements.append(self._parse_expr())
            self._expect(TokenType.RBRACKET, "Expected ']'")
            return ast.ListLit(elements=elements)

        if self._match(TokenType.LBRACE):
            return self._parse_record()

        if self._match(TokenType.IDENT):
            name = self.tokens[self.pos - 1].value
            return ast.Var(name=name)

        raise ParseError(f"Unexpected token: {self._current().type}", self._current())

    def _parse_lambda(self) -> ast.Lambda:
        params = []

        if self._match(TokenType.LPAREN):
            params.append(self._parse_param())
            while self._match(TokenType.COMMA):
                params.append(self._parse_param())
            self._expect(TokenType.RPAREN, "Expected ')'")
        else:
            while self._check(TokenType.IDENT) and self._peek().type in (
                TokenType.IDENT,
                TokenType.FAT_ARROW,
                TokenType.COLON,
                TokenType.LPAREN,
            ):
                if self._check(TokenType.IDENT):
                    params.append(self._parse_param())
                else:
                    break

        self._expect(TokenType.FAT_ARROW, "Expected '=>'")
        body = self._parse_expr()

        return ast.Lambda(params=params, body=body)

    def _parse_record(self) -> ast.Expr:
        if self._check(TokenType.IDENT) and self._peek().type == TokenType.KW_WITH:
            base_name = self._expect(TokenType.IDENT, "Expected record name")
            self._expect(TokenType.KW_WITH, "Expected 'with'")
            updates = []
            while not self._check(TokenType.RBRACE):
                field_name = self._expect(TokenType.IDENT, "Expected field name")
                self._expect(TokenType.EQUALS, "Expected '='")
                value = self._parse_expr()
                updates.append(ast.RecordField(name=field_name.value, value=value))
                if not self._match(TokenType.COMMA):
                    break
            self._expect(TokenType.RBRACE, "Expected '}'")
            return ast.RecordUpdate(
                record=ast.Var(name=base_name.value),
                updates=updates,
            )

        fields = []
        if not self._check(TokenType.RBRACE):
            while True:
                field_name = self._expect(TokenType.IDENT, "Expected field name")
                self._expect(TokenType.COLON, "Expected ':'")
                value = self._parse_expr()
                fields.append(ast.RecordField(name=field_name.value, value=value))
                if not self._match(TokenType.COMMA):
                    break

        self._expect(TokenType.RBRACE, "Expected '}'")
        return ast.RecordLit(fields=fields)

    def _parse_interface(self) -> ast.InterfaceDecl:
        name_token = self._expect(TokenType.IDENT, "Expected interface name")
        name = name_token.value

        params = []
        if self._check(TokenType.IDENT):
            params.append(self._current().value)
            self.pos += 1
            while self._check(TokenType.IDENT):
                params.append(self._current().value)
                self.pos += 1

        self._expect(TokenType.KW_WHERE, "Expected 'where'")
        self._expect(TokenType.LBRACE, "Expected '{'")

        methods = []
        while not self._check(TokenType.RBRACE):
            method_name_token = self._expect(TokenType.IDENT, "Expected method name")
            self._expect(TokenType.COLON, "Expected ':'")
            method_type = self._parse_type_ref()
            methods.append(
                ast.InterfaceMethod(name=method_name_token.value, type=method_type)
            )
            if not self._match(TokenType.COMMA):
                break

        self._expect(TokenType.RBRACE, "Expected '}'")
        return ast.InterfaceDecl(name=name, params=params, methods=methods)

    def _parse_impl(self) -> ast.ImplDecl:
        class_name_token = self._expect(TokenType.IDENT, "Expected class name")
        class_name = class_name_token.value

        type_ref = self._parse_type_ref()

        self._expect(TokenType.KW_WHERE, "Expected 'where'")
        self._expect(TokenType.LBRACE, "Expected '{'")

        methods = []
        while not self._check(TokenType.RBRACE):
            method_name_token = self._expect(TokenType.IDENT, "Expected method name")
            params = []
            if self._match(TokenType.LPAREN):
                if not self._check(TokenType.RPAREN):
                    params.append(self._parse_param())
                    while self._match(TokenType.COMMA):
                        params.append(self._parse_param())
                self._expect(TokenType.RPAREN, "Expected ')'")
            else:
                while self._check(TokenType.IDENT):
                    param_token = self._expect(
                        TokenType.IDENT, "Expected parameter name"
                    )
                    params.append(ast.Param(name=str(param_token.value)))
            self._expect(TokenType.EQUALS, "Expected '='")
            body = self._parse_expr()
            methods.append(
                ast.ImplMethod(name=method_name_token.value, params=params, body=body)
            )
            if not self._match(TokenType.COMMA):
                break

        self._expect(TokenType.RBRACE, "Expected '}'")
        return ast.ImplDecl(class_name=class_name, type_ref=type_ref, methods=methods)

    def _parse_effect(self) -> ast.EffectDecl:
        name_token = self._expect(TokenType.IDENT, "Expected effect name")
        name = name_token.value

        type_param = None
        if self._check(TokenType.IDENT):
            type_param = str(self._current().value)
            self.pos += 1

        self._expect(TokenType.LBRACE, "Expected '{'")

        operations = []
        while not self._check(TokenType.RBRACE):
            op_name_token = self._expect(TokenType.IDENT, "Expected operation name")
            self._expect(TokenType.COLON, "Expected ':'")
            op_type = self._parse_type_ref()
            operations.append(ast.EffectOp(name=op_name_token.value, type=op_type))
            if not self._match(TokenType.COMMA):
                break

        self._expect(TokenType.RBRACE, "Expected '}'")
        return ast.EffectDecl(name=name, operations=operations)
