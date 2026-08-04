from __future__ import annotations

from datetime import datetime
from nephon_graph.core.contexts import Context, ContextConstraint, ContextConstraintKind


class ContextAlgebra:
    """
    Context algebra handling matching, compatibility, refinement, and premise context intersection.
    Truth Table:
    - EXACT(a) ∩ EXACT(b) = EXACT(a) if a == b else EMPTY
    - ANY ∩ x = x
    - UNKNOWN ∩ UNKNOWN = UNKNOWN
    - UNKNOWN ∩ ANY = UNKNOWN
    - UNKNOWN ∩ EXACT(x) = INDETERMINATE (non-applicable / prevents automatic application)
    """

    @staticmethod
    def intersect_constraint(
        c1: ContextConstraint, c2: ContextConstraint
    ) -> ContextConstraint | None:
        """
        Intersects two dimension constraints.
        Returns:
        - ContextConstraint: valid intersection
        - None: EMPTY (incompatible / disjoint)
        """
        # If either is ANY, result is the other
        if c1.kind == ContextConstraintKind.ANY:
            return c2
        if c2.kind == ContextConstraintKind.ANY:
            return c1

        # If both are UNKNOWN
        if c1.kind == ContextConstraintKind.UNKNOWN and c2.kind == ContextConstraintKind.UNKNOWN:
            return ContextConstraint.unknown()

        # If one is UNKNOWN and the other EXACT -> INDETERMINATE (fails automatic match / return None)
        if (
            (c1.kind == ContextConstraintKind.UNKNOWN and c2.kind == ContextConstraintKind.EXACT)
            or (c2.kind == ContextConstraintKind.UNKNOWN and c1.kind == ContextConstraintKind.EXACT)
        ):
            return None  # INDETERMINATE / non-applicable

        # Both are EXACT
        if c1.kind == ContextConstraintKind.EXACT and c2.kind == ContextConstraintKind.EXACT:
            if c1.value == c2.value:
                return c1
            return None  # EMPTY / disjoint

        return None

    @classmethod
    def are_compatible(cls, c1: Context, c2: Context) -> bool:
        """
        Checks if two Contexts overlap without producing EMPTY or INDETERMINATE dimensions.
        Also verifies temporal window overlap.
        """
        dimensions = ["project", "environment", "operation", "perspective", "authority", "ontology_version"]
        for dim in dimensions:
            cons1: ContextConstraint = getattr(c1, dim)
            cons2: ContextConstraint = getattr(c2, dim)
            if cls.intersect_constraint(cons1, cons2) is None:
                return False

        # Check temporal overlap
        # Temporal open-interval semantics: None = -infinity for valid_from, +infinity for valid_until
        # Overlap exists if max(start1, start2) <= min(end1, end2)
        start1 = c1.valid_from or datetime.min
        start2 = c2.valid_from or datetime.min
        end1 = c1.valid_until or datetime.max
        end2 = c2.valid_until or datetime.max

        max_start = max(start1, start2)
        min_end = min(end1, end2)

        return max_start <= min_end

    @classmethod
    def intersect_contexts(cls, c1: Context, c2: Context) -> Context | None:
        """
        Computes the narrowest common Context intersection of c1 and c2.
        Returns None if any dimension intersection is EMPTY or INDETERMINATE.
        """
        if not cls.are_compatible(c1, c2):
            return None

        project = cls.intersect_constraint(c1.project, c2.project)
        environment = cls.intersect_constraint(c1.environment, c2.environment)
        operation = cls.intersect_constraint(c1.operation, c2.operation)
        perspective = cls.intersect_constraint(c1.perspective, c2.perspective)
        authority = cls.intersect_constraint(c1.authority, c2.authority)
        ontology_version = cls.intersect_constraint(c1.ontology_version, c2.ontology_version)

        if not all([project, environment, operation, perspective, authority, ontology_version]):
            return None

        start1 = c1.valid_from or datetime.min
        start2 = c2.valid_from or datetime.min
        end1 = c1.valid_until or datetime.max
        end2 = c2.valid_until or datetime.max

        max_start = max(start1, start2)
        min_end = min(end1, end2)

        valid_from = None if max_start == datetime.min else max_start
        valid_until = None if min_end == datetime.max else min_end

        return Context(
            project=project,
            environment=environment,
            operation=operation,
            perspective=perspective,
            authority=authority,
            ontology_version=ontology_version,
            valid_from=valid_from,
            valid_until=valid_until,
        )
