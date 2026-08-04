from __future__ import annotations

from nephon_graph.core.contexts import Context, ContextConstraint
from nephon_graph.engine.context_algebra import ContextAlgebra


def test_context_constraint_intersection():
    c_any = ContextConstraint.any()
    c_exact_prod = ContextConstraint.exact("production")
    c_exact_dev = ContextConstraint.exact("development")
    c_unknown = ContextConstraint.unknown()

    # ANY ∩ EXACT(prod) = EXACT(prod)
    res1 = ContextAlgebra.intersect_constraint(c_any, c_exact_prod)
    assert res1 is not None and res1.kind == "exact" and res1.value == "production"

    # EXACT(prod) ∩ EXACT(dev) = None (EMPTY)
    res2 = ContextAlgebra.intersect_constraint(c_exact_prod, c_exact_dev)
    assert res2 is None

    # UNKNOWN ∩ UNKNOWN = UNKNOWN
    res3 = ContextAlgebra.intersect_constraint(c_unknown, c_unknown)
    assert res3 is not None and res3.kind == "unknown"

    # UNKNOWN ∩ EXACT(prod) = None (INDETERMINATE / non-applicable)
    res4 = ContextAlgebra.intersect_constraint(c_unknown, c_exact_prod)
    assert res4 is None


def test_context_compatibility_and_intersection():
    ctx1 = Context(environment=ContextConstraint.exact("production"))
    ctx2 = Context(environment=ContextConstraint.exact("production"))
    ctx3 = Context(environment=ContextConstraint.exact("development"))

    assert ContextAlgebra.are_compatible(ctx1, ctx2) is True
    assert ContextAlgebra.are_compatible(ctx1, ctx3) is False

    intersected = ContextAlgebra.intersect_contexts(ctx1, ctx2)
    assert intersected is not None
    assert intersected.environment.value == "production"
