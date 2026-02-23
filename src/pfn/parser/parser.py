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
        module_name = None

        # Handle optional module declaration at the start
        if self._match(TokenType.KW_MODULE):
            name_token = self._expect(TokenType.IDENT, "Expected module name")
            module_name = str(name_token.value)
            # Handle dotted module names (e.g., Bootstrap.Token)
            while self._match(TokenType.DOT):
                part_token = self._expect(TokenType.IDENT, "Expected module name part")
                module_name = module_name + "." + str(part_token.value)

        while not self._check(TokenType.EOF):
            decl = self._parse_declaration()
            if decl is not None:
                declarations.append(decl)
        return ast.Module(name=module_name, declarations=declarations)

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

        # Accept keywords as function names (e.g., `def match(...)`)
        name_token = self._match(
            TokenType.IDENT,
            TokenType.KW_MODULE,
            TokenType.KW_TYPE,
            TokenType.KW_DATA,
            TokenType.KW_DEF,
            TokenType.KW_LET,
            TokenType.KW_IN,
            TokenType.KW_IF,
            TokenType.KW_THEN,
            TokenType.KW_ELSE,
            TokenType.KW_MATCH,
            TokenType.KW_WITH,
            TokenType.KW_INTERFACE,
            TokenType.KW_IMPL,
            TokenType.KW_IMPORT,
            TokenType.KW_EXPORT,
            TokenType.KW_AS,
            TokenType.KW_EFFECT,
            TokenType.KW_HANDLER,
            TokenType.KW_HANDLE,
            TokenType.KW_DO,
            TokenType.KW_FORALL,
            TokenType.KW_EXISTS,
            TokenType.KW_FAMILY,
            TokenType.KW_WHERE,
            TokenType.KW_FN,
            TokenType.KW_GADT,
        )
        if not name_token:
            name_token = self._expect(TokenType.IDENT, "Expected function name")
        name = name_token.value

        params = []
        while True:
            if self._match(TokenType.LPAREN):
                if not self._check(TokenType.RPAREN):
                    params.append(self._parse_param())
                    while self._match(TokenType.COMMA):
                        params.append(self._parse_param())
                self._expect(TokenType.RPAREN, "Expected ')' after parameters")
            elif self._check(TokenType.IDENT) or self._check(TokenType.UNDERSCORE):
                params.append(self._parse_param())
            else:
                break

        return_type = None
        if self._match(TokenType.COLON):
            return_type = self._parse_type_ref()
        elif self._match(TokenType.ARROW):
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
        # Accept IDENT, UNDERSCORE, or keywords as parameter name
        if self._check(TokenType.UNDERSCORE):
            name_token = self._match(TokenType.UNDERSCORE)
            name = "_"
        else:
            name_token = self._match(
                TokenType.IDENT,
                TokenType.KW_MODULE,
                TokenType.KW_TYPE,
                TokenType.KW_DATA,
                TokenType.KW_DEF,
                TokenType.KW_LET,
                TokenType.KW_IN,
                TokenType.KW_IF,
                TokenType.KW_THEN,
                TokenType.KW_ELSE,
                TokenType.KW_MATCH,
                TokenType.KW_WITH,
                TokenType.KW_INTERFACE,
                TokenType.KW_IMPL,
                TokenType.KW_IMPORT,
                TokenType.KW_EXPORT,
                TokenType.KW_AS,
                TokenType.KW_EFFECT,
                TokenType.KW_HANDLER,
                TokenType.KW_HANDLE,
                TokenType.KW_DO,
                TokenType.KW_FORALL,
                TokenType.KW_EXISTS,
                TokenType.KW_FAMILY,
                TokenType.KW_WHERE,
                TokenType.KW_FN,
                TokenType.KW_GADT,
            )
            if not name_token:
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
            while (
                self._check(TokenType.IDENT) or self._check(TokenType.LPAREN)
            ) and not self._check(TokenType.PIPE, TokenType.EOF):
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

    def _peek_n(self, n: int) -> Token:
        if self.pos + n >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + n]

    def _is_binding_pattern(self) -> bool:
        """Check if current position starts a new let binding pattern.
        
        A binding pattern is: IDENT followed by optional IDENTs (params) and then EQUALS.
        Examples:
        - name = ...        (simple binding)
        - name param = ...  (function binding)
        """
        if not self._check(TokenType.IDENT):
            return False
        # Get the line number of the first IDENT
        first_token = self._current()
        if not hasattr(first_token, 'span') or not first_token.span:
            return False
        first_line = first_token.span.line
        
        idx = 1
        while self._peek_n(idx).type == TokenType.IDENT:
            # Check if this IDENT is on the same line
            peek_token = self._peek_n(idx)
            if hasattr(peek_token, 'span') and peek_token.span:
                if peek_token.span.line != first_line:
                    # Different line - this is not a binding pattern
                    return False
            idx += 1
        
        # Check if the token after all IDENTs is EQUALS and on the same line
        equals_token = self._peek_n(idx)
        if hasattr(equals_token, 'span') and equals_token.span:
            if equals_token.span.line != first_line:
                return False
        
        # This is a binding pattern if we see IDENT followed by IDENT(s) and then EQUALS
        return equals_token.type == TokenType.EQUALS

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

        if self._match(TokenType.LPAREN):
            exposing = []
            if self._match(TokenType.DOUBLE_DOT):
                exposing = [".."]
            elif not self._check(TokenType.RPAREN):
                name_token = self._expect(TokenType.IDENT, "Expected import name")
                name = str(name_token.value)
                if self._match(TokenType.LPAREN):
                    if self._match(TokenType.DOUBLE_DOT):
                        name = f"{name}(..)"
                    else:
                        inner = []
                        inner_token = self._expect(
                            TokenType.IDENT, "Expected constructor name"
                        )
                        inner.append(str(inner_token.value))
                        while self._match(TokenType.COMMA):
                            inner_token = self._expect(
                                TokenType.IDENT, "Expected constructor name"
                            )
                            inner.append(str(inner_token.value))
                        name = f"{name}({', '.join(inner)})"
                    self._expect(
                        TokenType.RPAREN, "Expected ')' after constructor list"
                    )
                exposing.append(name)
                while self._match(TokenType.COMMA):
                    name_token = self._expect(TokenType.IDENT, "Expected import name")
                    name = str(name_token.value)
                    if self._match(TokenType.LPAREN):
                        if self._match(TokenType.DOUBLE_DOT):
                            name = f"{name}(..)"
                        else:
                            inner = []
                            inner_token = self._expect(
                                TokenType.IDENT, "Expected constructor name"
                            )
                            inner.append(str(inner_token.value))
                            while self._match(TokenType.COMMA):
                                inner_token = self._expect(
                                    TokenType.IDENT, "Expected constructor name"
                                )
                                inner.append(str(inner_token.value))
                            name = f"{name}({', '.join(inner)})"
                        self._expect(
                            TokenType.RPAREN, "Expected ')' after constructor list"
                        )
                    exposing.append(name)
            self._expect(TokenType.RPAREN, "Expected ')' after import list")

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
        while self._check(TokenType.IDENT) or self._check(TokenType.LPAREN):
            args.append(self._parse_type_atom())
        if args:
            if isinstance(base, ast.SimpleTypeRef):
                return ast.SimpleTypeRef(name=base.name, args=args)
        return base

    def _parse_type_atom(self) -> ast.TypeRef:
        if self._match(TokenType.LPAREN):
            if self._match(TokenType.RPAREN):
                return ast.TupleTypeRef(elements=[])
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
                    field_name = self._match(
                        TokenType.IDENT,
                        TokenType.KW_MODULE,
                        TokenType.KW_TYPE,
                        TokenType.KW_DATA,
                        TokenType.KW_DEF,
                        TokenType.KW_LET,
                        TokenType.KW_IN,
                        TokenType.KW_IF,
                        TokenType.KW_THEN,
                        TokenType.KW_ELSE,
                        TokenType.KW_MATCH,
                        TokenType.KW_WITH,
                        TokenType.KW_INTERFACE,
                        TokenType.KW_IMPL,
                        TokenType.KW_IMPORT,
                        TokenType.KW_EXPORT,
                        TokenType.KW_AS,
                        TokenType.KW_EFFECT,
                        TokenType.KW_HANDLER,
                        TokenType.KW_HANDLE,
                        TokenType.KW_DO,
                        TokenType.KW_FORALL,
                        TokenType.KW_EXISTS,
                        TokenType.KW_FAMILY,
                        TokenType.KW_WHERE,
                        TokenType.KW_FN,
                        TokenType.KW_GADT,
                    )
                    if not field_name:
                        field_name = self._expect(
                            TokenType.IDENT, "Expected field name"
                        )
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
            bindings = []
            while True:
                if self._check(TokenType.LPAREN):
                    pattern = self._parse_pattern()
                    self._expect(TokenType.EQUALS, "Expected '=' after let pattern")
                    value = self._parse_expr()
                    bindings.append(
                        ast.LetPattern(pattern=pattern, value=value, body=None)
                    )
                elif self._match(TokenType.UNDERSCORE):
                    name = "_"
                    params = []
                    while self._check(TokenType.IDENT):
                        params.append(self._parse_param())

                    self._expect(TokenType.EQUALS, "Expected '=' after let binding")
                    value = self._parse_expr()

                    if params:
                        bindings.append(
                            ast.LetFunc(
                                name=name, params=params, value=value, body=None
                            )
                        )
                    else:
                        bindings.append(ast.Let(name=name, value=value, body=None))
                else:
                    name_token = self._expect(TokenType.IDENT, "Expected variable name")
                    name = name_token.value

                    params = []
                    while self._check(TokenType.IDENT):
                        params.append(self._parse_param())

                    self._expect(TokenType.EQUALS, "Expected '=' after let binding")
                    value = self._parse_expr()

                    if params:
                        bindings.append(
                            ast.LetFunc(
                                name=name, params=params, value=value, body=None
                            )
                        )
                    else:
                        bindings.append(ast.Let(name=name, value=value, body=None))

                if self._match(TokenType.KW_LET):
                    continue
                # Check for next binding: IDENT followed by IDENT (function params) or EQUALS
                if self._check(TokenType.IDENT):
                    # Look ahead to see if this is a new binding
                    next_pos = self.pos + 1
                    if next_pos < len(self.tokens):
                        next_token = self.tokens[next_pos]
                        # Continue if: IDENT IDENT (function) or IDENT EQUALS (value)
                        if next_token.type in (TokenType.IDENT, TokenType.EQUALS):
                            continue
                if self._check(TokenType.LPAREN):
                    continue
                break

            self._match(TokenType.KW_IN)
            body = self._parse_expr()

            for binding in reversed(bindings):
                binding.body = body
                body = binding

            return body

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
            if self._match(TokenType.PIPE):
                pass
            while True:
                pattern = self._parse_pattern()
                guard = None
                if self._match(TokenType.KW_IF):
                    guard = self._parse_expr()
                self._expect(TokenType.ARROW, "Expected '->'")
                body = self._parse_expr_stop_on_pattern()
                cases.append(ast.MatchCase(pattern=pattern, guard=guard, body=body))
                if self._match(TokenType.PIPE):
                    continue
                if self._is_pattern_start() and self._peek().type == TokenType.ARROW:
                    continue
                if self._is_pattern_start():
                    saved_pos = self.pos
                    try:
                        self._parse_pattern()
                        if self._check(TokenType.ARROW):
                            self.pos = saved_pos
                            continue
                    except:
                        pass
                    self.pos = saved_pos
                break
            return ast.Match(scrutinee=scrutinee, cases=cases)
        return self._parse_or()

    def _parse_expr_stop_on_pattern(self) -> ast.Expr:
        return self._parse_let_stop_on_pattern()

    def _parse_let_stop_on_pattern(self) -> ast.Expr:
        if self._match(TokenType.KW_LET):
            bindings = []
            while True:
                if self._check(TokenType.LPAREN):
                    pattern = self._parse_pattern()
                    self._expect(TokenType.EQUALS, "Expected '=' after let pattern")
                    value = self._parse_expr_stop_on_pattern()
                    bindings.append(
                        ast.LetPattern(pattern=pattern, value=value, body=None)
                    )
                elif self._match(TokenType.UNDERSCORE):
                    name = "_"
                    params = []
                    while self._check(TokenType.IDENT):
                        params.append(self._parse_param())

                    self._expect(TokenType.EQUALS, "Expected '=' after let binding")
                    value = self._parse_expr_stop_on_pattern()

                    if params:
                        bindings.append(
                            ast.LetFunc(
                                name=name, params=params, value=value, body=None
                            )
                        )
                    else:
                        bindings.append(ast.Let(name=name, value=value, body=None))
                else:
                    name_token = self._expect(TokenType.IDENT, "Expected variable name")
                    name = name_token.value

                    params = []
                    while self._check(TokenType.IDENT):
                        params.append(self._parse_param())

                    self._expect(TokenType.EQUALS, "Expected '=' after let binding")
                    value = self._parse_expr_stop_on_pattern()

                    if params:
                        bindings.append(
                            ast.LetFunc(
                                name=name, params=params, value=value, body=None
                            )
                        )
                    else:
                        bindings.append(ast.Let(name=name, value=value, body=None))

                if self._match(TokenType.KW_LET):
                    continue
                # Check for next binding: IDENT followed by IDENT (function params) or EQUALS
                if self._check(TokenType.IDENT):
                    # Look ahead to see if this is a new binding
                    next_pos = self.pos + 1
                    if next_pos < len(self.tokens):
                        next_token = self.tokens[next_pos]
                        # Continue if: IDENT IDENT (function) or IDENT EQUALS (value)
                        if next_token.type in (TokenType.IDENT, TokenType.EQUALS):
                            continue
                if self._check(TokenType.LPAREN):
                    continue
                break

            self._match(TokenType.KW_IN)
            body = self._parse_expr_stop_on_pattern()

            for binding in reversed(bindings):
                binding.body = body
                body = binding

            return body

        if self._match(TokenType.KW_DO):
            return self._parse_do()

        return self._parse_if_stop_on_pattern()

    def _parse_if_stop_on_pattern(self) -> ast.Expr:
        if self._match(TokenType.KW_IF):
            cond = self._parse_expr_stop_on_pattern()
            self._expect(TokenType.KW_THEN, "Expected 'then'")
            then_branch = self._parse_expr_stop_on_pattern()
            self._expect(TokenType.KW_ELSE, "Expected 'else'")
            else_branch = self._parse_expr_stop_on_pattern()
            return ast.If(cond=cond, then_branch=then_branch, else_branch=else_branch)
        if (
            self._check(TokenType.KW_MATCH)
            and not self._peek().type == TokenType.LPAREN
        ):
            self._match(TokenType.KW_MATCH)
            return self._parse_match_stop_on_pattern()
        return self._parse_or()

    def _parse_match_stop_on_pattern(self) -> ast.Expr:
        scrutinee = self._parse_expr_stop_on_pattern()
        self._expect(TokenType.KW_WITH, "Expected 'with'")
        cases = []
        if self._match(TokenType.PIPE):
            pass
        while True:
            pattern = self._parse_pattern()
            guard = None
            if self._match(TokenType.KW_IF):
                guard = self._parse_expr_stop_on_pattern()
            self._expect(TokenType.ARROW, "Expected '->'")
            body = self._parse_expr_stop_on_pattern()
            cases.append(ast.MatchCase(pattern=pattern, guard=guard, body=body))
            if self._match(TokenType.PIPE):
                continue
            if self._is_pattern_start() and self._peek().type == TokenType.ARROW:
                continue
            if self._is_pattern_start():
                saved_pos = self.pos
                try:
                    self._parse_pattern()
                    if self._check(TokenType.ARROW):
                        self.pos = saved_pos
                        continue
                except:
                    pass
                self.pos = saved_pos
            break
        return ast.Match(scrutinee=scrutinee, cases=cases)

    def _is_pattern_start(self) -> bool:
        return self._check(
            TokenType.INT,
            TokenType.FLOAT,
            TokenType.STRING,
            TokenType.CHAR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.UNDERSCORE,
            TokenType.LBRACKET,
            TokenType.LPAREN,
            TokenType.IDENT,
        )

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
            first = self._parse_pattern()
            if self._match(TokenType.PIPE):
                tail = self._parse_pattern()
                self._expect(TokenType.RBRACKET, "Expected ']'")
                return ast.ConsPattern(head=first, tail=tail)
            elements = [first]
            while self._match(TokenType.COMMA):
                if self._match(TokenType.TRIPLE_DOT):
                    rest = self._parse_pattern()
                    self._expect(TokenType.RBRACKET, "Expected ']'")
                    return ast.ListPattern(elements=elements, rest=rest)
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
        if self._match(
            TokenType.IDENT,
            TokenType.KW_DATA,
            TokenType.KW_TYPE,
            TokenType.KW_DEF,
            TokenType.KW_LET,
            TokenType.KW_IN,
            TokenType.KW_IF,
            TokenType.KW_THEN,
            TokenType.KW_ELSE,
            TokenType.KW_MATCH,
            TokenType.KW_WITH,
            TokenType.KW_INTERFACE,
            TokenType.KW_IMPL,
            TokenType.KW_IMPORT,
            TokenType.KW_EXPORT,
            TokenType.KW_MODULE,
            TokenType.KW_AS,
            TokenType.KW_EFFECT,
            TokenType.KW_HANDLER,
            TokenType.KW_HANDLE,
            TokenType.KW_DO,
            TokenType.KW_FORALL,
            TokenType.KW_EXISTS,
            TokenType.KW_FAMILY,
            TokenType.KW_WHERE,
            TokenType.KW_FN,
            TokenType.KW_GADT,
        ):
            name = self.tokens[self.pos - 1].value
            if self._check(TokenType.LPAREN):
                args = []
                self.pos += 1
                if not self._check(TokenType.RPAREN):
                    args.append(self._parse_pattern())
                    while self._match(TokenType.COMMA):
                        args.append(self._parse_pattern())
                self._expect(TokenType.RPAREN, "Expected ')'")
                return ast.ConstructorPattern(name=name, args=args)
            name_str = str(name)
            if name_str and name_str[0].isupper():
                args = []
                while self._is_pattern_start():
                    if (
                        self._check(TokenType.IDENT)
                        and self._peek().type == TokenType.EQUALS
                    ):
                        break
                    if (
                        self._check(TokenType.IDENT)
                        and self._peek().type == TokenType.DOT
                    ):
                        break
                    args.append(self._parse_atom_pattern())
                return ast.ConstructorPattern(name=name, args=args)
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
                if self._check(TokenType.RPAREN):
                    self._expect(TokenType.RPAREN, "Expected ')'")
                    expr = ast.App(func=expr, args=[])
                    expr = self._parse_access_from(expr)
                    continue
                saved_pos = self.pos
                try:
                    first = self._parse_expr()
                    if self._match(TokenType.COMMA):
                        elements = [first]
                        while not self._check(TokenType.RPAREN):
                            elements.append(self._parse_expr())
                            if not self._match(TokenType.COMMA):
                                break
                        self._expect(TokenType.RPAREN, "Expected ')'")
                        if self._check(TokenType.EQUALS):
                            self.pos = saved_pos - 1
                            break
                        for arg in elements:
                            expr = ast.App(func=expr, args=[arg])
                        expr = self._parse_access_from(expr)
                    else:
                        self._expect(TokenType.RPAREN, "Expected ')'")
                        if self._check(TokenType.EQUALS):
                            self.pos = saved_pos - 1
                            break
                        expr = ast.App(func=expr, args=[first])
                        expr = self._parse_access_from(expr)
                except ParseError:
                    self.pos = saved_pos
                    break
            elif self._check(TokenType.IDENT) and self._peek().type == TokenType.EQUALS:
                break
            elif self._is_binding_pattern():
                break
            elif self._is_pattern_start() and self._peek().type == TokenType.ARROW:
                break
            elif self._check(TokenType.IDENT):
                name = self._current().value
                if name and str(name)[0].isupper():
                    if self._peek().type == TokenType.LPAREN:
                        saved_pos = self.pos
                        self.pos += 2  # Skip IDENT and LPAREN
                        depth = 1
                        while depth > 0 and not self._check(TokenType.EOF):
                            if self._match(TokenType.LPAREN):
                                depth += 1
                            elif self._match(TokenType.RPAREN):
                                depth -= 1
                            else:
                                self.pos += 1
                        is_arrow = self._check(TokenType.ARROW)
                        self.pos = saved_pos
                        if is_arrow:
                            break
                    elif self._peek().type == TokenType.ARROW:
                        break
                arg = self._parse_atom()
                expr = ast.App(func=expr, args=[arg])
            elif self._check(
                TokenType.INT,
                TokenType.FLOAT,
                TokenType.STRING,
                TokenType.CHAR,
                TokenType.TRUE,
                TokenType.FALSE,
                TokenType.LBRACE,
                TokenType.BACKSLASH,
            ):
                arg = self._parse_atom()
                expr = ast.App(func=expr, args=[arg])
            elif self._check(TokenType.LBRACKET):
                saved_pos = self.pos
                self.pos += 1
                has_pipe = False
                depth = 1
                while depth > 0 and not self._check(TokenType.EOF):
                    if self._match(TokenType.LBRACKET):
                        depth += 1
                    elif self._match(TokenType.RBRACKET):
                        depth -= 1
                    elif self._match(TokenType.PIPE) and depth == 1:
                        has_pipe = True
                    else:
                        self.pos += 1
                is_arrow = self._check(TokenType.ARROW)
                self.pos = saved_pos
                if has_pipe or is_arrow:
                    break
                arg = self._parse_atom()
                expr = ast.App(func=expr, args=[arg])
            else:
                break

        return expr

    def _parse_access_from(self, expr: ast.Expr) -> ast.Expr:
        while True:
            if self._match(TokenType.DOT):
                if self._match(
                    TokenType.IDENT,
                    TokenType.KW_DATA,
                    TokenType.KW_TYPE,
                    TokenType.KW_DEF,
                    TokenType.KW_LET,
                    TokenType.KW_IN,
                    TokenType.KW_IF,
                    TokenType.KW_THEN,
                    TokenType.KW_ELSE,
                    TokenType.KW_MATCH,
                    TokenType.KW_WITH,
                    TokenType.KW_INTERFACE,
                    TokenType.KW_IMPL,
                    TokenType.KW_IMPORT,
                    TokenType.KW_EXPORT,
                    TokenType.KW_MODULE,
                    TokenType.KW_AS,
                    TokenType.KW_EFFECT,
                    TokenType.KW_HANDLER,
                    TokenType.KW_HANDLE,
                    TokenType.KW_DO,
                    TokenType.KW_FORALL,
                    TokenType.KW_EXISTS,
                    TokenType.KW_FAMILY,
                    TokenType.KW_WHERE,
                    TokenType.KW_FN,
                    TokenType.KW_GADT,
                ):
                    field_name = self.tokens[self.pos - 1].value
                    expr = ast.FieldAccess(expr=expr, field=field_name)
                else:
                    raise ParseError("Expected field name", self._current())
            else:
                break
        return expr

    def _parse_access(self) -> ast.Expr:
        expr = self._parse_atom()

        while True:
            if self._match(TokenType.DOT):
                if self._match(
                    TokenType.IDENT,
                    TokenType.KW_DATA,
                    TokenType.KW_TYPE,
                    TokenType.KW_DEF,
                    TokenType.KW_LET,
                    TokenType.KW_IN,
                    TokenType.KW_IF,
                    TokenType.KW_THEN,
                    TokenType.KW_ELSE,
                    TokenType.KW_MATCH,
                    TokenType.KW_WITH,
                    TokenType.KW_INTERFACE,
                    TokenType.KW_IMPL,
                    TokenType.KW_IMPORT,
                    TokenType.KW_EXPORT,
                    TokenType.KW_MODULE,
                    TokenType.KW_AS,
                    TokenType.KW_EFFECT,
                    TokenType.KW_HANDLER,
                    TokenType.KW_HANDLE,
                    TokenType.KW_DO,
                    TokenType.KW_FORALL,
                    TokenType.KW_EXISTS,
                    TokenType.KW_FAMILY,
                    TokenType.KW_WHERE,
                    TokenType.KW_FN,
                    TokenType.KW_GADT,
                ):
                    field_name = self.tokens[self.pos - 1].value
                    expr = ast.FieldAccess(expr=expr, field=field_name)
                else:
                    raise ParseError("Expected field name", self._current())
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

        if self._match(TokenType.BACKSLASH):
            return self._parse_backslash_lambda()

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

        if self._match(
            TokenType.IDENT,
            TokenType.KW_MATCH,
            TokenType.KW_DATA,
            TokenType.KW_TYPE,
            TokenType.KW_DEF,
            TokenType.KW_LET,
            TokenType.KW_IN,
            TokenType.KW_IF,
            TokenType.KW_THEN,
            TokenType.KW_ELSE,
            TokenType.KW_WITH,
            TokenType.KW_INTERFACE,
            TokenType.KW_IMPL,
            TokenType.KW_IMPORT,
            TokenType.KW_EXPORT,
            TokenType.KW_MODULE,
            TokenType.KW_AS,
            TokenType.KW_EFFECT,
            TokenType.KW_HANDLER,
            TokenType.KW_HANDLE,
            TokenType.KW_DO,
            TokenType.KW_FORALL,
            TokenType.KW_EXISTS,
            TokenType.KW_FAMILY,
            TokenType.KW_WHERE,
            TokenType.KW_FN,
            TokenType.KW_GADT,
        ):
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

    def _parse_backslash_lambda(self) -> ast.Lambda:
        params = []

        while self._check(TokenType.IDENT) or self._check(TokenType.UNDERSCORE):
            params.append(self._parse_param())

        self._expect(TokenType.ARROW, "Expected '->' after lambda parameters")
        body = self._parse_expr()

        return ast.Lambda(params=params, body=body)

    def _parse_record(self) -> ast.Expr:
        if self._check(TokenType.IDENT):
            base = ast.Var(
                name=self._expect(TokenType.IDENT, "Expected record name").value
            )
            while self._match(TokenType.DOT):
                field = self._expect(TokenType.IDENT, "Expected field name")
                base = ast.FieldAccess(expr=base, field=field.value)
            if self._match(TokenType.KW_WITH):
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
                    record=base,
                    updates=updates,
                )
            elif self._match(TokenType.COLON):
                value = self._parse_expr()
                fields = [ast.RecordField(name=base.name, value=value)]
                while self._match(TokenType.COMMA):
                    field_name = self._match(
                        TokenType.IDENT,
                        TokenType.KW_MODULE,
                        TokenType.KW_TYPE,
                        TokenType.KW_DATA,
                        TokenType.KW_DEF,
                        TokenType.KW_LET,
                        TokenType.KW_IN,
                        TokenType.KW_IF,
                        TokenType.KW_THEN,
                        TokenType.KW_ELSE,
                        TokenType.KW_MATCH,
                        TokenType.KW_WITH,
                        TokenType.KW_INTERFACE,
                        TokenType.KW_IMPL,
                        TokenType.KW_IMPORT,
                        TokenType.KW_EXPORT,
                        TokenType.KW_AS,
                        TokenType.KW_EFFECT,
                        TokenType.KW_HANDLER,
                        TokenType.KW_HANDLE,
                        TokenType.KW_DO,
                        TokenType.KW_FORALL,
                        TokenType.KW_EXISTS,
                        TokenType.KW_FAMILY,
                        TokenType.KW_WHERE,
                        TokenType.KW_FN,
                        TokenType.KW_GADT,
                    )
                    if not field_name:
                        field_name = self._expect(
                            TokenType.IDENT, "Expected field name"
                        )
                    self._expect(TokenType.COLON, "Expected ':'")
                    value = self._parse_expr()
                    fields.append(ast.RecordField(name=field_name.value, value=value))
                self._expect(TokenType.RBRACE, "Expected '}'")
                return ast.RecordLit(fields=fields)
            else:
                self._expect(TokenType.RBRACE, "Expected '}', ':', or 'with'")

        fields = []
        if not self._check(TokenType.RBRACE):
            while True:
                field_name = self._match(
                    TokenType.IDENT,
                    TokenType.KW_MODULE,
                    TokenType.KW_TYPE,
                    TokenType.KW_DATA,
                    TokenType.KW_DEF,
                    TokenType.KW_LET,
                    TokenType.KW_IN,
                    TokenType.KW_IF,
                    TokenType.KW_THEN,
                    TokenType.KW_ELSE,
                    TokenType.KW_MATCH,
                    TokenType.KW_WITH,
                    TokenType.KW_INTERFACE,
                    TokenType.KW_IMPL,
                    TokenType.KW_IMPORT,
                    TokenType.KW_EXPORT,
                    TokenType.KW_AS,
                    TokenType.KW_EFFECT,
                    TokenType.KW_HANDLER,
                    TokenType.KW_HANDLE,
                    TokenType.KW_DO,
                    TokenType.KW_FORALL,
                    TokenType.KW_EXISTS,
                    TokenType.KW_FAMILY,
                    TokenType.KW_WHERE,
                    TokenType.KW_FN,
                    TokenType.KW_GADT,
                )
                if not field_name:
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
