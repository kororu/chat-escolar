import main
from content_reader import detect_subject_from_question, normalize_question


def test_quick_action_recovers_last_question_from_conversation(monkeypatch):
    monkeypatch.setattr(main, "get_recent_conversation_items", lambda *_: [{"question": "que es una metafora"}])
    monkeypatch.setattr(
        main,
        "retrieve_local_content",
        lambda *_args, **_kwargs: {"results": [{"title": "Lenguaje figurado en narraciones", "path": "", "course": "6° básico", "subject": "Lenguaje", "metadata": {}}]},
    )
    response = main.chat_quick_action(main.QuickActionRequest(
        action="Dame un ejemplo", course="5° básico", subject="Lenguaje", conversation_id="test",
    ))
    assert "tiempo es oro" in response["answer"].lower()
    assert "Falta un tema previo" not in response["answer"]


def test_metaphor_variants_normalize_to_language():
    for question in (
        "\u00bfQu\u00e9 es una met\u00e1fora?",
        "que es una metafora?",
        "que es metafora?",
        "explicame metafora",
    ):
        analysis = normalize_question(question)
        assert analysis["possible_topic"] == "metafora"
        assert "metafora" in analysis["normalized_text"]
        assert detect_subject_from_question(question) == ("Lenguaje", 1.0)
