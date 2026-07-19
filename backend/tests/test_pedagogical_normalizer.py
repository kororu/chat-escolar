from pedagogical_normalizer import clean_pedagogical_lines, detect_intent


def test_normalizer_removes_editorial_scaffolding():
    text = "Una fracción representa partes iguales.\nAplicar el concepto al ejemplo.\nComprobar la respuesta."
    assert clean_pedagogical_lines(text) == "Una fracción representa partes iguales."


def test_intent_keeps_concept_request_type():
    assert detect_intent("Dame un ejemplo de sustantivo") == "example"
    assert detect_intent("¿Qué es una fracción?") == "definition"
