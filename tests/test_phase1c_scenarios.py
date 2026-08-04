from pathlib import Path
import pytest

from nephon_graph.core.belief import BeliefStatus, ProvenanceSupportStatus
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.compiler.kanon_compiler import KanonCompiler, MarkdownLoader
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.engine.governance_policy import GovernancePolicy, GovernanceDisposition
from nephon_graph.engine.inference_engine import InferenceEngine
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.event_store import InMemoryEventStore
from experiments.phase1c_decisions.scenarios import (
    build_scenario_1_dev_recovery,
    build_scenario_2_prod_firewall,
    build_scenario_3_missing_evidence,
)


@pytest.fixture
def compiled_kanon_store() -> tuple[InMemoryEventStore, any]:
    store = InMemoryEventStore()
    compiler = KanonCompiler(store)

    kanon_dir = Path(__file__).parent.parent / "data" / "00-kanon"
    compilation_res = compiler.compile_directory(kanon_dir)
    return store, compilation_res


def test_scenario_2_prod_firewall_end_to_end_and_isolated_ablation(compiled_kanon_store):
    store, compiler_res = compiled_kanon_store
    scenario = build_scenario_2_prod_firewall(compiler_res, store)

    # 1. Resolve constitutional declaration IDs to compiled claim UUIDs
    const_claim_ids = [compiler_res.declaration_claim_ids[dec_id] for dec_id in scenario.constitutional_declaration_ids]
    fact_claim_ids = [c.id for c in scenario.fact_claims]
    all_premise_ids = const_claim_ids + fact_claim_ids

    # 2. Register rule and derive decision claim
    rule = scenario.inference_rules[0]
    engine = InferenceEngine(store)
    engine.register_rule(rule)

    derived_claim = engine.derive_claim(
        rule_id=rule.rule_id,
        rule_version=rule.version,
        premise_claim_ids=all_premise_ids,
        conclusion_atom=scenario.decision_atom,
        polarity=scenario.expected_polarity,
        asserted_by="ScenarioTest",
    )

    # 3. Evaluate belief and governance on main store
    belief = BeliefEvaluator.evaluate(scenario.decision_atom.id, scenario.query_context, store)
    assert belief.status == scenario.expected_belief

    policy = GovernancePolicy()
    gov_decision = policy.evaluate(
        claims=store.get_claims_for_atom(scenario.decision_atom.id),
        context=scenario.query_context,
        belief_state=belief,
        predicate=scenario.decision_atom.predicate,
    )
    assert gov_decision.disposition == scenario.expected_governance_disposition

    # 4. Execute Isolated EventStore Snapshot Causal-Ablation Test
    forked_store = store.fork()

    # Retract AUT-04 on forked snapshot branch
    aut04_claim_id = compiler_res.declaration_claim_ids["AUT-04"]
    retract_event = KnowledgeEvent(
        aggregate_id=str(aut04_claim_id),
        aggregate_version=3,
        event_type="ClaimRetracted",
        payload={"claim_id": str(aut04_claim_id), "reason": "Causal ablation test"},
    )
    forked_store.append(retract_event)

    # Verify AUT-04 is inactive on forked store, but active on main store
    assert forked_store.is_claim_active(aut04_claim_id) is False
    assert store.is_claim_active(aut04_claim_id) is True

    # Re-evaluate derived claim provenance on forked snapshot branch
    forked_prov_status = ProvenanceEvaluator.evaluate(derived_claim.provenance, forked_store)
    assert forked_prov_status == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED

    # Re-evaluate derived claim provenance on main store (must remain VALID)
    main_prov_status = ProvenanceEvaluator.evaluate(derived_claim.provenance, store)
    assert main_prov_status == ProvenanceSupportStatus.VALID

    # Epistemic status on forked branch drops to UNKNOWN
    forked_belief = BeliefEvaluator.evaluate(scenario.decision_atom.id, scenario.query_context, forked_store)
    assert forked_belief.status == BeliefStatus.UNKNOWN


def test_scenario_1_dev_recovery_end_to_end_and_isolated_ablation(compiled_kanon_store):
    store, compiler_res = compiled_kanon_store
    scenario = build_scenario_1_dev_recovery(compiler_res, store)

    const_claim_ids = [compiler_res.declaration_claim_ids[dec_id] for dec_id in scenario.constitutional_declaration_ids]
    fact_claim_ids = [c.id for c in scenario.fact_claims]
    all_premise_ids = const_claim_ids + fact_claim_ids

    rule = scenario.inference_rules[0]
    engine = InferenceEngine(store)
    engine.register_rule(rule)

    derived_claim = engine.derive_claim(
        rule_id=rule.rule_id,
        rule_version=rule.version,
        premise_claim_ids=all_premise_ids,
        conclusion_atom=scenario.decision_atom,
        polarity=scenario.expected_polarity,
        asserted_by="ScenarioTest",
    )

    belief = BeliefEvaluator.evaluate(scenario.decision_atom.id, scenario.query_context, store)
    assert belief.status == scenario.expected_belief

    policy = GovernancePolicy()
    gov_decision = policy.evaluate(
        claims=store.get_claims_for_atom(scenario.decision_atom.id),
        context=scenario.query_context,
        belief_state=belief,
        predicate=scenario.decision_atom.predicate,
    )
    assert gov_decision.disposition == scenario.expected_governance_disposition

    # Isolated snapshot ablation test
    forked_store = store.fork()
    aut03_claim_id = compiler_res.declaration_claim_ids["AUT-03"]
    forked_store.append(
        KnowledgeEvent(
            aggregate_id=str(aut03_claim_id),
            aggregate_version=3,
            event_type="ClaimRetracted",
            payload={"claim_id": str(aut03_claim_id)},
        )
    )
    assert ProvenanceEvaluator.evaluate(derived_claim.provenance, forked_store) == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED
    assert ProvenanceEvaluator.evaluate(derived_claim.provenance, store) == ProvenanceSupportStatus.VALID


def test_scenario_3_missing_evidence_end_to_end_and_isolated_ablation(compiled_kanon_store):
    store, compiler_res = compiled_kanon_store
    scenario = build_scenario_3_missing_evidence(compiler_res, store)

    const_claim_ids = [compiler_res.declaration_claim_ids[dec_id] for dec_id in scenario.constitutional_declaration_ids]
    fact_claim_ids = [c.id for c in scenario.fact_claims]
    all_premise_ids = const_claim_ids + fact_claim_ids

    rule = scenario.inference_rules[0]
    engine = InferenceEngine(store)
    engine.register_rule(rule)

    derived_claim = engine.derive_claim(
        rule_id=rule.rule_id,
        rule_version=rule.version,
        premise_claim_ids=all_premise_ids,
        conclusion_atom=scenario.decision_atom,
        polarity=scenario.expected_polarity,
        asserted_by="ScenarioTest",
    )

    belief = BeliefEvaluator.evaluate(scenario.decision_atom.id, scenario.query_context, store)
    assert belief.status == scenario.expected_belief

    policy = GovernancePolicy()
    gov_decision = policy.evaluate(
        claims=store.get_claims_for_atom(scenario.decision_atom.id),
        context=scenario.query_context,
        belief_state=belief,
        predicate=scenario.decision_atom.predicate,
    )
    assert gov_decision.disposition == scenario.expected_governance_disposition

    # Isolated snapshot ablation test
    forked_store = store.fork()
    epi03_claim_id = compiler_res.declaration_claim_ids["EPI-03"]
    forked_store.append(
        KnowledgeEvent(
            aggregate_id=str(epi03_claim_id),
            aggregate_version=3,
            event_type="ClaimRetracted",
            payload={"claim_id": str(epi03_claim_id)},
        )
    )
    assert ProvenanceEvaluator.evaluate(derived_claim.provenance, forked_store) == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED
    assert ProvenanceEvaluator.evaluate(derived_claim.provenance, store) == ProvenanceSupportStatus.VALID
