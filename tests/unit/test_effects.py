from pfn.effects import (
    Effect,
    IOEffect,
    StateEffect,
    ThrowEffect,
    EffectSet,
    PURE,
    IOHandler,
    StateHandler,
    ThrowHandler,
    run_io,
    run_state,
    run_throw,
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
