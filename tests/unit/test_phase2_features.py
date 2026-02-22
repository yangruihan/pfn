from pfn.types import (
    TCon,
    TConstraint,
    TExists,
    TFloat,
    TForall,
    TFun,
    TInt,
    TList,
    TQualified,
    TRowPoly,
    TString,
    TTuple,
    TVar,
    Scheme,
    Subst,
)
from pfn.typechecker.classes import (
    ClassContext,
    create_default_context,
    check_constraint,
    solve_constraints,
    build_dictionary,
)
from pfn.typechecker.exhaustiveness import (
    PWild,
    PVar,
    PCon,
    PInt,
    PBool,
    PList,
    PTuple,
    check_exhaustiveness,
    pattern_to_string,
    format_missing_patterns,
)
from pfn.typechecker.rows import (
    Row,
    row_empty,
    row_extend,
    row_restrict,
    row_has_field,
    row_labels,
)


class TestAdvancedTypes:
    def test_tforall_creation(self):
        t = TForall(("a",), TFun(TVar("a"), TVar("a")))
        assert "forall" in str(t)
        assert "a" in str(t)

    def test_texists_creation(self):
        t = TExists(("a",), TVar("a"))
        assert "exists" in str(t)
        assert "a" in str(t)

    def test_tconstraint_creation(self):
        t = TConstraint("Eq", TInt())
        assert str(t) == "Eq Int"

    def test_tqualified_creation(self):
        t = TQualified(
            (TConstraint("Eq", TVar("a")),),
            TFun(TVar("a"), TVar("a")),
        )
        assert "Eq" in str(t)
        assert "=>" in str(t)

    def test_trowpoly_creation(self):
        t = TRowPoly({"name": TString(), "age": TInt()})
        assert "name" in str(t)
        assert "age" in str(t)

    def test_trowpoly_with_rest(self):
        t = TRowPoly({"name": TString()}, "r")
        assert "|" in str(t)
        assert "r" in str(t)

    def test_scheme_with_constraints(self):
        s = Scheme(
            ("a",),
            TFun(TVar("a"), TVar("a")),
            (TConstraint("Eq", TVar("a")),),
        )
        assert "Eq" in str(s)
        assert "forall" in str(s)


class TestSubstAdvanced:
    def test_apply_tforall(self):
        s = Subst({"a": TInt()})
        t = TForall(("b",), TFun(TVar("b"), TVar("a")))
        result = s.apply(t)
        assert isinstance(result, TForall)
        assert result.inner == TFun(TVar("b"), TInt())

    def test_apply_tconstraint(self):
        s = Subst({"a": TInt()})
        t = TConstraint("Eq", TVar("a"))
        result = s.apply(t)
        assert result.type_ == TInt()

    def test_apply_tqualified(self):
        s = Subst({"a": TInt()})
        t = TQualified(
            (TConstraint("Show", TVar("a")),),
            TVar("a"),
        )
        result = s.apply(t)
        assert result.constraints[0].type_ == TInt()
        assert result.inner == TInt()

    def test_apply_trowpoly(self):
        s = Subst({"a": TInt()})
        t = TRowPoly({"x": TVar("a")})
        result = s.apply(t)
        assert result.fields["x"] == TInt()

    def test_free_vars_tforall(self):
        s = Subst()
        t = TForall(("a",), TFun(TVar("a"), TVar("b")))
        fvs = s.free_vars(t)
        assert "b" in fvs
        assert "a" not in fvs

    def test_free_vars_trowpoly(self):
        s = Subst()
        t = TRowPoly({"x": TVar("a")}, "r")
        fvs = s.free_vars(t)
        assert "a" in fvs
        assert "r" in fvs


class TestTypeClassSystem:
    def test_create_default_context(self):
        ctx = create_default_context()
        assert ctx.lookup_class("Eq") is not None
        assert ctx.lookup_class("Ord") is not None
        assert ctx.lookup_class("Show") is not None
        assert ctx.lookup_class("Functor") is not None
        assert ctx.lookup_class("Monad") is not None
        assert ctx.lookup_class("Num") is not None

    def test_superclass_relationship(self):
        ctx = create_default_context()
        ord_class = ctx.lookup_class("Ord")
        assert ord_class is not None
        assert "Eq" in ord_class.superclasses

    def test_get_all_superclasses(self):
        ctx = create_default_context()
        supers = ctx.get_all_superclasses("Monad")
        assert "Applicative" in supers
        assert "Functor" in supers

    def test_check_constraint(self):
        ctx = create_default_context()
        constraint = TConstraint("Eq", TInt())
        assert check_constraint(ctx, constraint)

    def test_solve_constraints(self):
        ctx = create_default_context()
        constraints = (
            TConstraint("Eq", TInt()),
            TConstraint("Show", TInt()),
        )
        assert solve_constraints(ctx, constraints, Subst())

    def test_build_dictionary(self):
        ctx = create_default_context()
        d = build_dictionary(ctx, "Eq", TInt())
        assert d is not None
        assert "eq" in d
        assert "neq" in d


class TestExhaustiveness:
    def test_exhaustive_wildcard(self):
        result = check_exhaustiveness([PWild()])
        assert result.exhaustive
        assert len(result.missing_patterns) == 0

    def test_exhaustive_bool(self):
        from pfn.types import TBool

        result = check_exhaustiveness([PCon("True"), PCon("False")], TBool())
        assert result.exhaustive

    def test_non_exhaustive_bool(self):
        from pfn.types import TBool

        result = check_exhaustiveness([PCon("True")], TBool())
        assert not result.exhaustive
        assert len(result.missing_patterns) == 1

    def test_redundant_pattern(self):
        result = check_exhaustiveness([PWild(), PInt(1)])
        assert result.exhaustive
        assert 1 in result.redundant_patterns

    def test_pattern_to_string(self):
        assert pattern_to_string(PWild()) == "_"
        assert pattern_to_string(PVar("x")) == "x"
        assert pattern_to_string(PInt(42)) == "42"
        assert pattern_to_string(PBool(True)) == "True"
        assert pattern_to_string(PCon("Some", (PInt(1),))) == "Some 1"

    def test_format_missing_patterns(self):
        missing = [PBool(True), PBool(False)]
        formatted = format_missing_patterns(missing)
        assert "True" in formatted
        assert "False" in formatted


class TestRowPolymorphism:
    def test_row_empty(self):
        r = row_empty()
        assert len(r.fields) == 0
        assert r.rest is None

    def test_row_extend(self):
        r = row_empty()
        r = row_extend(r, "name", TString())
        assert row_has_field(r, "name")
        assert r.fields["name"] == TString()

    def test_row_restrict(self):
        r = row_empty()
        r = row_extend(r, "name", TString())
        r = row_extend(r, "age", TInt())
        r = row_restrict(r, "age")
        assert row_has_field(r, "name")
        assert not row_has_field(r, "age")

    def test_row_labels(self):
        r = row_empty()
        r = row_extend(r, "name", TString())
        r = row_extend(r, "age", TInt())
        labels = row_labels(r)
        assert "name" in labels
        assert "age" in labels

    def test_row_with_rest(self):
        r = Row({"name": TString()}, "r")
        assert r.rest == "r"
        assert row_has_field(r, "name")


class TestRankNTypes:
    def test_rank1_type(self):
        t = TForall(("a",), TFun(TVar("a"), TVar("a")))
        assert isinstance(t, TForall)
        assert t.vars == ("a",)

    def test_rank2_type(self):
        inner = TForall(("a",), TFun(TVar("a"), TVar("a")))
        t = TFun(inner, TTuple((TInt(), TString())))
        assert isinstance(t, TFun)
        assert isinstance(t.param, TForall)

    def test_nested_forall(self):
        t = TForall(("a",), TForall(("b",), TFun(TVar("a"), TVar("b"))))
        assert t.vars == ("a",)
        assert isinstance(t.inner, TForall)
