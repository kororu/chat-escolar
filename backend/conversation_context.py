from dataclasses import dataclass

try:
    from .content_reader import normalize_question, normalize_text
except ImportError:
    from content_reader import normalize_question, normalize_text


FOLLOW_UP_PHRASES = {
    "cual fue el mas usado",
    "y el mas grande",
    "y el mas fuerte",
    "por que paso eso",
    "como funcionaba",
    "dame otro ejemplo",
    "y despues que ocurrio",
    "y ese",
    "y eso",
    "cual era",
    "como era",
}


def is_follow_up_question(normalized_question: str) -> bool:
    return normalized_question in FOLLOW_UP_PHRASES


def describe_topic(analysis: dict) -> str | None:
    topic = analysis.get("possible_topic")
    normalized_question = analysis.get("normalized_text", "")

    if topic == "tanques" and "segunda guerra" in normalized_question:
        return "tanques durante la Segunda Guerra Mundial"
    if topic == "segunda guerra mundial":
        return "la Segunda Guerra Mundial"
    if topic == "ecosistemas":
        return "ecosistema"
    return topic


def reconstruct_follow_up(question: str, topic: str) -> str:
    normalized_question = normalize_text(question)
    normalized_topic = normalize_text(topic)

    if normalized_question == "cual fue el mas usado":
        if normalized_topic == "tanques durante la segunda guerra mundial":
            return "cual fue el tanque mas usado durante la segunda guerra mundial"
        return f"cual fue el mas usado de {topic}"
    if normalized_question == "dame otro ejemplo":
        return f"dame otro ejemplo de {topic}"
    if normalized_question == "y el mas grande":
        return f"cual fue el mas grande de {topic}"
    if normalized_question == "y el mas fuerte":
        return f"cual fue el mas fuerte de {topic}"
    if normalized_question == "por que paso eso":
        return f"por que paso eso en {topic}"
    if normalized_question == "como funcionaba":
        return f"como funcionaba {topic}"
    if normalized_question == "y despues que ocurrio":
        return f"y despues que ocurrio en {topic}"
    if normalized_question in {"y ese", "y eso", "cual era", "como era"}:
        return f"{normalized_question} en {topic}"
    return normalized_question


def build_conversation_context(question: str, recent_items: list[dict]) -> dict:
    analysis = normalize_question(question)
    normalized_question = analysis["normalized_text"]
    follow_up = is_follow_up_question(normalized_question)

    if not follow_up:
        return {
            "normalized_question": normalized_question,
            "contextual_question": normalized_question,
            "active_topic": describe_topic(analysis),
            "confidence": 1.0,
            "used_context": False,
            "requires_clarification": False,
            "query_analysis": analysis,
        }

    for index, item in enumerate(recent_items[:6]):
        topic = item.get("active_topic")
        if not topic:
            continue
        confidence = 0.92 if index == 0 else max(0.72, 0.88 - (index * 0.04))
        return {
            "normalized_question": normalized_question,
            "contextual_question": reconstruct_follow_up(normalized_question, topic),
            "active_topic": topic,
            "confidence": confidence,
            "used_context": True,
            "requires_clarification": False,
            "query_analysis": analysis,
        }

    return {
        "normalized_question": normalized_question,
        "contextual_question": normalized_question,
        "active_topic": None,
        "confidence": 0.0,
        "used_context": False,
        "requires_clarification": True,
        "query_analysis": analysis,
    }
