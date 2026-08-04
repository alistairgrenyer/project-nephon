from __future__ import annotations

from uuid import uuid4
import pytest

from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.storage.base import ConcurrencyError, EventIntegrityError
from nephon_graph.storage.event_store import InMemoryEventStore


def test_event_store_idempotency_and_integrity():
    store = InMemoryEventStore()
    event_id = uuid4()

    ev1 = KnowledgeEvent(
        event_id=event_id,
        aggregate_id="agg-1",
        aggregate_version=1,
        event_type="TestEvent",
        payload={"key": "val"},
    )

    # 1. First append succeeds
    appended1 = store.append(ev1)
    assert appended1.sequence == 1

    # 2. Identical event re-submission succeeds idempotently (NO-OP)
    ev1_copy = KnowledgeEvent(
        event_id=event_id,
        aggregate_id="agg-1",
        aggregate_version=1,
        event_type="TestEvent",
        occurred_at=appended1.occurred_at,
        payload={"key": "val"},
    )
    appended2 = store.append(ev1_copy)
    assert appended2.sequence == 1

    # 3. Duplicate event_id with DIFFERENT payload raises EventIntegrityError
    ev1_corrupted = KnowledgeEvent(
        event_id=event_id,
        aggregate_id="agg-1",
        aggregate_version=1,
        event_type="TestEvent",
        occurred_at=appended1.occurred_at,
        payload={"key": "different_val"},
    )
    with pytest.raises(EventIntegrityError):
        store.append(ev1_corrupted)


def test_event_store_aggregate_versioning():
    store = InMemoryEventStore()

    ev1 = KnowledgeEvent(aggregate_id="agg-1", aggregate_version=1, event_type="E1")
    store.append(ev1)

    # Version jump (from 1 to 3) raises ConcurrencyError
    ev3 = KnowledgeEvent(aggregate_id="agg-1", aggregate_version=3, event_type="E3")
    with pytest.raises(ConcurrencyError):
        store.append(ev3)

    # Version 2 succeeds
    ev2 = KnowledgeEvent(aggregate_id="agg-1", aggregate_version=2, event_type="E2")
    store.append(ev2)
    assert store._aggregate_versions["agg-1"] == 2
