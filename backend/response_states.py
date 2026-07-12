LOCAL_VERIFIED = "local_verified"
LOCAL_RELATED = "local_related"
LOCAL_LOW_CONFIDENCE = "local_low_confidence"
NO_LOCAL_CONTENT = "no_local_content"
DEMO_FALLBACK = "demo_fallback"
CLARIFICATION_REQUIRED = "clarification_required"
OLLAMA_GENERATED = "ollama_generated"
OLLAMA_WITH_LOCAL_CONTENT = "ollama_with_local_content"
OLLAMA_UNAVAILABLE = "ollama_unavailable"
LOCAL_CONTENT_FALLBACK = "local_content_fallback"

RESPONSE_STATUSES = {
    LOCAL_VERIFIED,
    LOCAL_RELATED,
    LOCAL_LOW_CONFIDENCE,
    NO_LOCAL_CONTENT,
    DEMO_FALLBACK,
    CLARIFICATION_REQUIRED,
    OLLAMA_GENERATED,
    OLLAMA_WITH_LOCAL_CONTENT,
    OLLAMA_UNAVAILABLE,
    LOCAL_CONTENT_FALLBACK,
}

LOCAL_PROVENANCE_STATUSES = {
    LOCAL_VERIFIED,
    LOCAL_CONTENT_FALLBACK,
    LOCAL_RELATED,
    LOCAL_LOW_CONFIDENCE,
    NO_LOCAL_CONTENT,
}

PROVIDER_DEMO = "demo"
PROVIDER_LOCAL_CONTENT = "local_content"
PROVIDER_OLLAMA = "ollama"
PROVIDER_OLLAMA_WITH_LOCAL_CONTENT = "ollama_with_local_content"


def uses_verified_local_content(provenance_status: str) -> bool:
    return provenance_status in {LOCAL_VERIFIED, LOCAL_CONTENT_FALLBACK}
