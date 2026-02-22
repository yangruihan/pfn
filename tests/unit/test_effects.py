from pfn.effects import (
    Effect,
    IOEffect,
    StateEffect,
    ThrowEffect,
    ReadEffect,
    EffectSet,
    PURE,
    IOHandler,
    StateHandler,
    ThrowHandler,
    run_io,
    run_state,
    run_throw,
)
from pfn.effects.infer import (
    EffectInferer,
    EffectEnv,
    infer_effects,
    is_pure,
    get_effect_names,
)
from pfn.effects.handlers import (
    HandlerContext,
    HandlerRegistry,
    HandlerBuilder,
    handler,
    get_handler_registry,
)


class TestEffectRepresentation:
    def test_io_effect(self):
        eff = IOEffect()
        assert isinstance(eff, Effect)

    def test_state_effect(self):
        eff = StateEffect(int)
        assert eff.state_type == int

    def test_throw_effect(self):
        eff = ThrowEffect(str)
        assert eff.error_type == str


class TestEffectSet:
    def test_empty_effect_set_is_pure(self):
        assert str(PURE) == "Pure"

    def test_effect_set_union(self):
        s1 = EffectSet(frozenset({IOEffect()}))
        s2 = EffectSet(frozenset({StateEffect(int)}))
        combined = s1.union(s2)
        assert len(combined.effects) == 2

    def test_effect_set_contains(self):
        s = EffectSet(frozenset({IOEffect()}))
        assert s.contains(IOEffect())


class TestIOHandler:
    def test_io_handler_print(self):
        output = []
        handler = IOHandler(
            input_func=lambda x: "test",
            output_func=lambda x: output.append(x),
        )
        result = None

        def cont(_):
            nonlocal result
            result = "done"

        handler.handle("print", ["hello"], cont)
        assert output == ["hello"]

    def test_io_handler_input(self):
        handler = IOHandler(
            input_func=lambda x: "user input",
            output_func=lambda x: None,
        )
        result = None

        def cont(val):
            nonlocal result
            result = val

        handler.handle("input", ["prompt: "], cont)
        assert result == "user input"


class TestStateHandler:
    def test_state_handler_get(self):
        handler = StateHandler(42)
        result = None

        def cont(val):
            nonlocal result
            result = val

        handler.handle("get", [], cont)
        assert result == 42

    def test_state_handler_put(self):
        handler = StateHandler(0)
        result = None

        def cont(val):
            nonlocal result
            result = val

        handler.handle("put", [100], cont)
        assert handler.state == 100
        assert result is None


class TestRunners:
    def test_run_io(self):
        def action():
            return 42

        result = run_io(action)
        assert result == 42

    def test_run_state(self):
        def action():
            return "result"

        result, state = run_state(action, 0)
        assert result == "result"
        assert state == 0

    def test_run_throw_with_exception(self):
        def action():
            raise ValueError("test error")

        result = run_throw(action)
        assert isinstance(result, ValueError)
        assert str(result) == "test error"


class TestEffectInference:
    def test_infer_pure_int(self):
        from pfn.parser import ast

        expr = ast.IntLit(42)
        effects = infer_effects(expr)
        assert is_pure(expr)

    def test_infer_pure_string(self):
        from pfn.parser import ast

        expr = ast.StringLit("hello")
        assert is_pure(expr)

    def test_infer_pure_lambda(self):
        from pfn.parser import ast

        expr = ast.Lambda([ast.Param("x")], ast.Var("x"))
        assert is_pure(expr)

    def test_infer_pure_let(self):
        from pfn.parser import ast

        expr = ast.Let("x", ast.IntLit(1), ast.Var("x"))
        assert is_pure(expr)

    def test_infer_pure_if(self):
        from pfn.parser import ast

        expr = ast.If(ast.BoolLit(True), ast.IntLit(1), ast.IntLit(2))
        assert is_pure(expr)

    def test_infer_pure_list(self):
        from pfn.parser import ast

        expr = ast.ListLit([ast.IntLit(1), ast.IntLit(2)])
        assert is_pure(expr)

    def test_effect_env(self):
        env = EffectEnv()
        env = env.extend("x", PURE)
        result = env.lookup("x")
        assert result == PURE

    def test_get_effect_names(self):
        es = EffectSet(frozenset({IOEffect(), StateEffect(int)}))
        names = get_effect_names(es)
        assert "IO" in names
        assert "State" in names


class TestHandlerRegistry:
    def test_get_registry(self):
        registry = get_handler_registry()
        assert registry is not None

    def test_handler_builder(self):
        builder = handler("IO")

        @builder.handle("input")
        def handle_input(prompt, resume):
            return resume("test")

        ctx = builder.build()
        assert "input" in ctx.operations


class TestEffectInferer:
    def test_inferer_creation(self):
        inferer = EffectInferer()
        assert inferer.env is not None

    def test_inferer_register_effect(self):
        inferer = EffectInferer()
        inferer.register_effect("Custom", ["op1", "op2"])
        assert "Custom" in inferer.effect_decls
        assert "op1" in inferer.effect_decls["Custom"]

    def test_inferer_handler_stack(self):
        inferer = EffectInferer()
        inferer.push_handler("IO")
        assert inferer.check_effect_handled(IOEffect())
        inferer.pop_handler()
        assert not inferer.check_effect_handled(IOEffect())
