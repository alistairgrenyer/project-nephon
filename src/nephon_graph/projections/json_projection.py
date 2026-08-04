from __future__ import annotations

import json
from typing import Any
from nephon_graph.retrieval.retrieval_engine import ContextRetrievalPayload
from nephon_graph.storage.event_store import InMemoryEventStore


class JSONProjection:
    """
    Diagnostic JSON projection generator for kernel event state and retrieval payloads.
    """

    @staticmethod
    def export_retrieval_payload(payload: ContextRetrievalPayload) -> str:
        return json.dumps(payload.model_dump(mode="json"), indent=2)

    @staticmethod
    def export_event_stream(store: InMemoryEventStore) -> str:
        events = [e.model_dump(mode="json") for e in store.get_events()]
        return json.dumps(events, indent=2)
