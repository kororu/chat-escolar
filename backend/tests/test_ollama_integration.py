import unittest
from unittest.mock import patch

import main
from prompt_builder import clean_ollama_response


class OllamaIntegrationTests(unittest.TestCase):
    def setUp(self):
        main._ollama_status_cache = None
        main._ollama_status_checked_at = None

    def payload(self, question="que es la fotosintesis?", mode="Estudiar para el colegio"):
        return main.ChatDemoRequest(
            course="6° básico",
            subject="Ciencias Naturales",
            mode=mode,
            question=question,
        )

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_verified_source_uses_ollama_with_local_content(self, generate, status, _save):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.return_value = "Explicación corta:\nLa fotosíntesis usa luz."

        response = main.chat_demo(self.payload())

        self.assertEqual(response["provenance_status"], "ollama_with_local_content")
        self.assertEqual(response["provider"], "ollama_with_local_content")
        self.assertTrue(response["used_local_content"])
        self.assertTrue(generate.called)

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_ollama_error_uses_educational_local_fallback(self, generate, status, _save):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.side_effect = main.OllamaError("timeout")
        payload = main.ChatDemoRequest(
            course="5° básico",
            subject="Ciencias Naturales",
            mode="Estudiar para el colegio",
            question="explicame los alimentos saludables",
            user_name="Erik",
            user_role="Estudiante",
        )

        response = main.chat_demo(payload)

        self.assertEqual(response["provenance_status"], "local_content_fallback")
        self.assertEqual(response["provider"], "local_content")
        self.assertTrue(response["used_local_content"])
        self.assertTrue(response["content_sources"])
        self.assertIn("nutrientes", response["answer"].lower())
        self.assertIn("Ejemplo:", response["answer"])
        self.assertNotIn("Encontré una fuente local verificada", response["answer"])

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    def test_unavailable_ollama_uses_local_fallback_without_generation(self, status, _save):
        status.return_value = {"enabled": True, "available": False, "model": "qwen3.5:2b", "model_installed": False}

        response = main.chat_demo(self.payload())

        self.assertEqual(response["provenance_status"], "local_content_fallback")
        self.assertEqual(response["provider"], "local_content")

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_explorer_without_source_can_use_general_ollama(self, generate, status, _save):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.return_value = "Un asteroide es una roca que viaja por el espacio."

        response = main.chat_demo(self.payload("que es un asteroide?", "Explorar mis intereses"))

        self.assertEqual(response["provenance_status"], "ollama_generated")
        self.assertFalse(response["used_local_content"])

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_school_without_source_does_not_call_ollama(self, generate, status, _save):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}

        response = main.chat_demo(self.payload("que es un asteroide?"))

        self.assertEqual(response["provenance_status"], "no_local_content")
        generate.assert_not_called()

    @patch.object(main, "get_ollama_status")
    def test_ai_status_unavailable_is_controlled(self, status):
        status.return_value = {"enabled": True, "available": False, "model": "qwen3.5:2b", "model_installed": False, "models": [], "message": "Ollama no está disponible."}
        response = main.ai_status()
        self.assertFalse(response["available"])
        self.assertEqual(response["model"], "qwen3.5:2b")

    def test_cleaning_hides_thinking_blocks(self):
        answer = clean_ollama_response("<think>razonamiento privado</think>\nExplicación corta: lista.")
        self.assertNotIn("think", answer.lower())
        self.assertIn("Explicación corta", answer)


if __name__ == "__main__":
    unittest.main()
