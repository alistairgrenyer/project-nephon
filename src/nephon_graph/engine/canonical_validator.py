from __future__ import annotations

from pydantic import BaseModel, Field
from nephon_graph.core.interpretations import Interpretation
from nephon_graph.core.ontology import PredicateDefinition
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.storage.base import EventStore


class ValidationReport(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)


class CanonicalValidator:
    """
    Deterministic validator verifying candidate interpretations against predicate schemas and entity types.
    """

    def __init__(self, store: EventStore) -> None:
        self.store = store
        self.predicates: dict[str, PredicateDefinition] = {}

    def register_predicate(self, predicate_def: PredicateDefinition) -> None:
        self.predicates[predicate_def.name.strip().lower()] = predicate_def

    def validate_atom(self, atom: PropositionAtom) -> ValidationReport:
        errors: list[str] = []

        pred_name = atom.predicate.strip().lower()
        if pred_name not in self.predicates:
            errors.append(f"Predicate '{atom.predicate}' is not registered in ontology.")
            return ValidationReport(valid=False, errors=errors)

        pred_def = self.predicates[pred_name]
        expected_roles = {r.role_name.strip().lower() for r in pred_def.roles}
        provided_roles = set(atom.arguments.keys())

        missing_roles = expected_roles - provided_roles
        if missing_roles:
            errors.append(f"Missing required roles for predicate '{pred_name}': {sorted(missing_roles)}")

        return ValidationReport(valid=len(errors) == 0, errors=errors)

    def validate_interpretation(self, interpretation: Interpretation) -> ValidationReport:
        errors: list[str] = []
        atom = self.store.get_atom(interpretation.proposition_id)
        if atom is None:
            errors.append(f"Proposition atom '{interpretation.proposition_id}' not found.")
            return ValidationReport(valid=False, errors=errors)

        atom_report = self.validate_atom(atom)
        errors.extend(atom_report.errors)

        return ValidationReport(valid=len(errors) == 0, errors=errors)
