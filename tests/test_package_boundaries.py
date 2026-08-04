from __future__ import annotations

import sys
import pytest


def test_nephon_contracts_imports_have_no_core_dependencies():
    """
    Verifies that nephon_contracts can be imported cleanly without importing nephon_core.
    """
    # Remove nephon_core from loaded modules if present
    core_modules = [m for m in sys.modules if m.startswith("nephon_core")]
    for m in core_modules:
        del sys.modules[m]

    import nephon_contracts

    assert hasattr(nephon_contracts, "ActionRequest")
    assert hasattr(nephon_contracts, "ConstitutionalDecision")
    assert hasattr(nephon_contracts, "compute_nephon_canonical_json_v1")

    # Verify no nephon_core modules were loaded during nephon_contracts import
    loaded_core = [m for m in sys.modules if m.startswith("nephon_core")]
    assert len(loaded_core) == 0, f"nephon_contracts must not import nephon_core! Loaded: {loaded_core}"
