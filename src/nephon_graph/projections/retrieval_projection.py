from __future__ import annotations

from nephon_graph.retrieval.retrieval_engine import ContextRetrievalPayload


class RetrievalProjection:
    """
    Concise retrieval payload projection for LLM prompt context injection.
    """

    @staticmethod
    def format_for_llm_prompt(payload: ContextRetrievalPayload) -> str:
        return payload.prompt_context_text
