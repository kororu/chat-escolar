try:
    from .response_states import (
        PROVIDER_DEMO,
        PROVIDER_LOCAL_CONTENT,
        PROVIDER_OLLAMA,
        uses_verified_local_content,
    )
except ImportError:
    from response_states import (
        PROVIDER_DEMO,
        PROVIDER_LOCAL_CONTENT,
        PROVIDER_OLLAMA,
        uses_verified_local_content,
    )


def build_educational_context(
    payload,
    retrieval: dict,
    conversation_context: dict,
    profile_course: str | None = None,
) -> dict:
    provenance_status = retrieval["provenance_status"]
    provider = (
        PROVIDER_LOCAL_CONTENT
        if uses_verified_local_content(provenance_status)
        else PROVIDER_DEMO
    )

    return {
        "provider": provider,
        "future_provider": PROVIDER_OLLAMA,
        "course": payload.course,
        "active_course": payload.course,
        "profile_course": profile_course,
        "effective_course": retrieval.get("effective_course"),
        "source_course": retrieval.get("source_course"),
        "source_subject": retrieval.get("source_subject"),
        "found_in_other_course": retrieval.get("found_in_other_course", False),
        "subject": payload.subject,
        "mode": payload.mode,
        "question": payload.question,
        "provenance_status": provenance_status,
        "query_analysis": retrieval["query_analysis"],
        "conversation_context": conversation_context,
        "verified_sources": retrieval.get("results", []),
        "related_sources": retrieval.get("related_results", []),
    }
