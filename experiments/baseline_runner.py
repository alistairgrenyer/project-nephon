from __future__ import annotations

import json
from exp_01_repeated_paraphrases import run_experiment_01
from exp_02_independent_sources import run_experiment_02
from exp_03_contextual_permissions import run_experiment_03
from exp_04_conflicting_testimony import run_experiment_04
from exp_05_superseded_state import run_experiment_05
from exp_06_source_correction import run_experiment_06
from exp_07_rule_version_change import run_experiment_07


def run_baseline_harness():
    print("==========================================================================")
    print("  NEPHON SEMANTIC KERNEL VS NAIVE GRAPH TRAVERSAL BASELINE HARNESS  ")
    print("==========================================================================")

    res1 = run_experiment_01()
    res2 = run_experiment_02()
    res3 = run_experiment_03()
    res4 = run_experiment_04()
    res5 = run_experiment_05()
    res6 = run_experiment_06()
    res7 = run_experiment_07()

    # Naive graph simulation metrics on 10 paraphrases:
    # Naive graph creates 10 separate nodes and 10 separate edge relationships.
    naive_nodes = res1["expressions_count"]  # 10
    naive_edges = res1["expressions_count"]  # 10
    kernel_atoms = res1["atom_count"]         # 1
    duplicate_reduction_pct = ((naive_nodes - kernel_atoms) / naive_nodes) * 100.0

    invariants = {
        "Invariant 1: Zero False Contradiction": res3["false_contradiction_count"] == 0,
        "Invariant 2: Zero Stale Claim Leakage": res5["claim1_active"] is False and res5["claim2_active"] is True,
        "Invariant 3: Invalidation Completeness": res6["invalidation_successful"] is True,
        "Invariant 4: Surviving Derivation Recovery": res2["valid"] is True,
        "Invariant 5: Conflict Preservation": res4["is_conflicted"] is True,
        "Invariant 6: Rule Deactivation Integrity": res7["rule_deactivation_successful"] is True,
    }

    all_invariants_passed = all(invariants.values())

    report = f"""
# Nephon Phase 1 Semantic Kernel Baseline Comparative Report

## Summary of Results
- All Architectural Correctness Invariants Passed: **{all_invariants_passed}**
- Duplicate Compression Ratio: **{duplicate_reduction_pct:.1f}%** ({naive_nodes} naive nodes compressed to {kernel_atoms} canonical atom)

## Architectural Correctness Invariants Verification
| Invariant | Result |
| :--- | :--- |
| **1. Zero False Contradiction** | {'PASSED' if invariants['Invariant 1: Zero False Contradiction'] else 'FAILED'} |
| **2. Zero Stale Claim Leakage** | {'PASSED' if invariants['Invariant 2: Zero Stale Claim Leakage'] else 'FAILED'} |
| **3. Invalidation Completeness** | {'PASSED' if invariants['Invariant 3: Invalidation Completeness'] else 'FAILED'} |
| **4. Surviving Derivation Recovery** | {'PASSED' if invariants['Invariant 4: Surviving Derivation Recovery'] else 'FAILED'} |
| **5. Conflict Preservation** | {'PASSED' if invariants['Invariant 5: Conflict Preservation'] else 'FAILED'} |
| **6. Rule Deactivation Integrity** | {'PASSED' if invariants['Invariant 6: Rule Deactivation Integrity'] else 'FAILED'} |

## Experiment Breakdown
- **Exp 01 (Repeated Paraphrases)**: {res1['expressions_count']} raw expressions -> {res1['atom_count']} canonical atom
- **Exp 02 (Independent Sources)**: {res2['independent_sources_count']} independent support paths preserved (status: {res2['provenance_status']})
- **Exp 03 (Contextual Permissions)**: Dev ({res3['dev_status']}) vs Prod ({res3['prod_status']}) -> {res3['false_contradiction_count']} false contradictions
- **Exp 04 (Conflicting Testimony)**: Positive + Negative testimony -> {res4['status']} status
- **Exp 05 (Superseded Operational State)**: Initial ({res5['initial_status']}) -> Updated ({res5['updated_status']}), total events logged: {res5['total_events_in_history']}
- **Exp 06 (Source Correction)**: Retraction of source -> Derived claim status: {res6['updated_status']}
- **Exp 07 (Rule Version Change)**: Rule deactivation -> Derived claim status: {res7['rule_deactivated_status']}
"""

    print(report)
    return report


if __name__ == "__main__":
    run_baseline_harness()
