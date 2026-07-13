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

    @staticmethod
    def automatic_settings():
        return {
            "ai_mode": "automatic",
            "ollama_enabled": True,
            "ollama_model": "qwen3.5:2b",
            "ollama_timeout_seconds": 25,
        }

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_verified_source_uses_ollama_with_local_content(self, generate, status, _save, _settings):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.return_value = "Explicación corta:\nLa fotosíntesis usa luz."

        response = main.chat_demo(self.payload())

        self.assertEqual(response["provenance_status"], "ollama_with_local_content")
        self.assertEqual(response["provider"], "ollama_with_local_content")
        self.assertTrue(response["used_local_content"])
        self.assertTrue(generate.called)

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_ollama_error_uses_educational_local_fallback(self, generate, status, _save, _settings):
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
        self.assertEqual(response["answer"].count("Pregunta de práctica:"), 1)
        practice = response["answer"].split("Pregunta de práctica:", 1)[1]
        self.assertEqual(practice.count("¿"), 1)
        self.assertNotIn("CN05 OA", response["answer"])
        self.assertNotIn("Encontré una fuente local verificada", response["answer"])

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    def test_unavailable_ollama_uses_local_fallback_without_generation(self, status, _save, _settings):
        status.return_value = {"enabled": True, "available": False, "model": "qwen3.5:2b", "model_installed": False}

        response = main.chat_demo(self.payload())

        self.assertEqual(response["provenance_status"], "local_content_fallback")
        self.assertEqual(response["provider"], "local_content")

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_explorer_without_source_can_use_general_ollama(self, generate, status, _save, _settings):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.return_value = "Un asteroide es una roca que viaja por el espacio."

        response = main.chat_demo(self.payload("que es un asteroide?", "Explorar mis intereses"))

        self.assertEqual(response["provenance_status"], "ollama_generated")
        self.assertFalse(response["used_local_content"])

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_school_without_source_does_not_call_ollama(self, generate, status, _save, _settings):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}

        response = main.chat_demo(self.payload("que es un asteroide?"))

        self.assertEqual(response["provenance_status"], "no_local_content")
        generate.assert_not_called()

    @patch.object(main, "load_settings", return_value={
        "ai_mode": "basic",
        "ollama_enabled": False,
        "ollama_model": "qwen3.5:2b",
        "ollama_timeout_seconds": 25,
    })
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_cached_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_basic_mode_does_not_check_or_call_ollama(self, generate, status, _save, _settings):
        response = main.chat_demo(self.payload())

        self.assertEqual(response["ai_mode_used"], "basic")
        self.assertFalse(response["ollama_attempted"])
        self.assertEqual(response["provider"], "local_content")
        status.assert_not_called()
        generate.assert_not_called()

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_explore_only_skips_ollama_for_school_mode(self, generate, status, _save):
        settings = {
            "ai_mode": "explore_only",
            "ollama_enabled": True,
            "ollama_model": "qwen3.5:2b",
            "ollama_timeout_seconds": 25,
        }
        with patch.object(main, "load_settings", return_value=settings):
            response = main.chat_demo(self.payload())

        self.assertEqual(response["ai_mode_used"], "explore_only")
        self.assertFalse(response["ollama_attempted"])
        status.assert_not_called()
        generate.assert_not_called()

    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_automatic_mode_passes_configured_timeout_to_ollama(self, generate, status, _save):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.return_value = "La fotosíntesis usa luz."
        settings = {**self.automatic_settings(), "ollama_timeout_seconds": 15}
        with patch.object(main, "load_settings", return_value=settings):
            response = main.chat_demo(self.payload())

        self.assertTrue(response["ollama_attempted"])
        self.assertEqual(response["ollama"]["timeout_seconds"], 15)
        self.assertEqual(generate.call_args.kwargs["timeout_seconds"], 15)

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
