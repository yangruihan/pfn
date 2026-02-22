from pfn.typechecker.classes import (
    ClassContext,
    ClassInfo,
    InstanceInfo,
    get_default_context,
    resolve_instance,
)
from pfn.types import TCon


class TestClassContext:
    def test_default_classes_exist(self):
        ctx = get_default_context()
        assert "Eq" in ctx.classes
        assert "Ord" in ctx.classes
        assert "Show" in ctx.classes
        assert "Functor" in ctx.classes
        assert "Monad" in ctx.classes

    def test_class_info(self):
        ctx = get_default_context()
        eq_class = ctx.classes["Eq"]
        assert eq_class.name == "Eq"
        assert "a" in eq_class.params
        assert "eq" in eq_class.methods

    def test_add_instance(self):
        ctx = ClassContext()
        ctx.add_class("Eq", ["a"], {"eq": None})
        ctx.add_instance("Eq", TCon("Int"), {"eq": None})
        inst = ctx.lookup_instance("Eq", TCon("Int"))
        assert inst is not None
        assert inst.class_name == "Eq"
        assert inst.type_ == TCon("Int")

    def test_resolve_instance(self):
        ctx = get_default_context()
        inst = resolve_instance(ctx, "Eq", TCon("Int"))
        assert inst is not None
        assert inst.class_name == "Eq"

    def test_get_method(self):
        ctx = ClassContext()
        ctx.add_class("Show", ["a"], {"show": None})
        ctx.add_instance("Show", TCon("String"), {"show": "show_string_impl"})
        method = ctx.get_method("Show", TCon("String"), "show")
        assert method == "show_string_impl"
