from pfn.types import (
    Type,
    TInt,
    TFloat,
    TString,
    TBool,
    TVar,
    TFun,
    TList,
    TTuple,
    Scheme,
    TypeEnv,
    Subst,
    TypeClass,
    ClassInstance,
)


class TestTypeClassRepresentation:
    def test_type_class_creation(self):
        tc = TypeClass(
            name="Eq",
            params=["a"],
            methods={"eq": TFun(TVar("a"), TFun(TVar("a"), TBool()))},
        )
        assert tc.name == "Eq"
        assert "a" in tc.params

    def test_type_class_with_superclasses(self):
        tc = TypeClass(
            name="Ord",
            params=["a"],
            methods={"compare": TFun(TVar("a"), TFun(TVar("a"), TBool()))},
            superclasses=["Eq"],
        )
        assert "Eq" in tc.superclasses

    def test_class_instance(self):
        inst = ClassInstance(
            class_name="Eq",
            type_=TInt(),
            methods={},
        )
        assert inst.class_name == "Eq"
        assert inst.type_ == TInt()


class TestTypeClassUnification:
    def test_unify_with_type_class_constraint(self):
        pass


class TestTypeClassInference:
    def test_infer_type_class_method(self):
        pass
