LOCAL_VERIFIED = "local_verified"
LOCAL_RELATED = "local_related"
LOCAL_LOW_CONFIDENCE = "local_low_confidence"
NO_LOCAL_CONTENT = "no_local_content"
DEMO_FALLBACK = "demo_fallback"
CLARIFICATION_REQUIRED = "clarification_required"
OLLAMA_GENERATED = "ollama_generated"

RESPONSE_STATUSES = {
    LOCAL_VERIFIED,
    LOCAL_RELATED,
    LOCAL_LOW_CONFIDENCE,
    NO_LOCAL_CONTENT,
    DEMO_FALLBACK,
    CLARIFICATION_REQUIRED,
    OLLAMA_GENERATED,
}

LOCAL_PROVENANCE_STATUSES = {
    LOCAL_VERIFIED,
    LOCAL_RELATED,
    LOCAL_LOW_CONFIDENCE,
    NO_LOCAL_CONTENT,
}

PROVIDER_DEMO = "demo"
PROVIDER_LOCAL_CONTENT = "local_content"
PROVIDER_OLLAMA = "ollama"


def uses_verified_local_content(provenance_status: str) -> bool:
    return provenance_status == LOCAL_VERIFIED
