import unittest
from unittest.mock import patch

import main
import ollama_client
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
        self.assertEqual(response["ollama_status"], "ollama_success")
        self.assertTrue(response["used_local_content"])
        self.assertTrue(response["grounding_required"])
        self.assertTrue(response["grounded_source_available"])
        self.assertTrue(response["answer_grounded"])
        self.assertTrue(generate.called)
        prompt = generate.call_args.args[0]
        self.assertIn("Eres Nexo, un tutor escolar de Chat Escolar", prompt)
        self.assertIn("Responde únicamente usando la información incluida en FUENTE LOCAL", prompt)
        self.assertIn("No uses conocimiento general, memoria externa o interna ni datos externos", prompt)
        self.assertIn("No agregues personas, países, fechas, cargos, barcos", prompt)
        self.assertIn("No digas quién ganó si la fuente no lo indica", prompt)
        self.assertIn("No agregues enemigos o países no mencionados", prompt)
        self.assertIn("FUENTE_INSUFICIENTE", prompt)
        self.assertIn("fotosíntesis", prompt.lower())

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
        self.assertEqual(response["local_fallback_reason"], "ollama_failure")
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

        self.assertEqual(response["provenance_status"], "ollama_unverified")
        self.assertFalse(response["used_local_content"])
        self.assertFalse(response["grounding_required"])
        self.assertFalse(response["answer_grounded"])
        self.assertIn("Puede contener errores", response["answer_warning"])

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_automatic_school_without_source_blocks_ollama(self, generate, status, _save, _settings):
        status.return_value = {"enabled": True, "available": True, "model": "qwen3.5:2b", "model_installed": True}
        generate.return_value = "Explicacion corta: un asteroide es una roca espacial."

        response = main.chat_demo(self.payload("que es un asteroide?"))

        self.assertEqual(response["provenance_status"], "generation_blocked_unverified")
        self.assertFalse(response["local_content_found"])
        self.assertFalse(response["answer_grounded"])
        self.assertEqual(response["generation_blocked_reason"], "no_verified_local_source")
        self.assertIn("fuente curricular local verificada", response["answer"])
        status.assert_not_called()
        generate.assert_not_called()

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_clear_history_question_uses_safe_verified_local_answer(
        self, generate, status, _save, _settings
    ):
        status.return_value = {
            "enabled": True,
            "available": True,
            "model": "qwen3.5:2b",
            "model_installed": True,
        }
        generate.return_value = (
            "Explicación corta:\nEl Combate Naval de Iquique ocurrió el 21 de mayo de 1879."
        )
        payload = main.ChatDemoRequest(
            course="6° básico",
            subject="Automática",
            mode="Estudiar para el colegio",
            question="explicame en que consiste el combate naval de iquique",
        )

        response = main.chat_demo(payload)

        self.assertEqual(response["detected_subject"], "Historia")
        self.assertEqual(response["subject_used"], "Historia")
        self.assertEqual(response["provenance_status"], "local_verified")
        self.assertEqual(response["provider"], "local_safe")
        self.assertTrue(response["local_content_found"])
        self.assertFalse(response["ollama_attempted"])
        self.assertFalse(response["used_ollama"])
        self.assertEqual(response["ollama_status"], "grounded_local_policy")
        self.assertEqual(response["local_fallback_reason"], "grounded_history_policy")
        self.assertTrue(response["answer_grounded"])
        self.assertEqual(response["content_sources"][0]["title"], "Combate Naval de Iquique")
        self.assertIn("21 de mayo de 1879", response["answer"])
        self.assertNotIn("ecosistema", response["answer"].lower())
        self.assertIn("Guerra del Pac", response["answer"])
        self.assertIn("Esmeralda", response["answer"])
        self.assertIn("Arturo Prat", response["answer"])
        self.assertIn("Miguel Grau", response["answer"])
        self.assertIn("Hu", response["answer"])
        self.assertNotIn("corbeta chilena arturo prat", response["answer"].lower())
        self.assertNotIn("murieron ambos comandantes", response["answer"].lower())
        self.assertNotIn("miguel grau murio", response["answer"].lower())
        self.assertNotIn("bernardo", response["answer"].lower())
        self.assertNotIn("No tengo suficiente información local verificada", response["answer"])
        status.assert_not_called()
        generate.assert_not_called()
        for forbidden in ("segunda guerra", "alemania", "italia", "japón", "misiles", "1942"):
            self.assertNotIn(forbidden, response["answer"].lower())

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    @patch.object(main, "should_use_grounded_history_answer", return_value=False)
    def test_iquique_hallucination_is_blocked_and_uses_local_fallback(
        self, _history_policy, generate, status, _save, _settings
    ):
        status.return_value = {
            "enabled": True,
            "available": True,
            "model": "qwen3.5:2b",
            "model_installed": True,
        }
        generate.return_value = (
            "El monarca peruano Juan Manuel Balmaceda buscaba invadir Chile con una "
            "bandera de victoria, españoles, piratas, oro, convoy, barcos italianos y "
            "navieros británicos. Durante la Segunda Guerra Mundial, Alemania, Italia y "
            "Japón enviaron misiles en 1942, en el siglo XVIII."
        )
        payload = main.ChatDemoRequest(
            course="6° básico",
            subject="Automática",
            mode="Estudiar para el colegio",
            question="explicame en que consiste el combate naval de iquique",
        )

        response = main.chat_demo(payload)

        self.assertEqual(response["provenance_status"], "local_content_fallback")
        self.assertEqual(response["provider"], "local_content")
        self.assertEqual(response["ollama_status"], "grounding_validation_failed")
        self.assertEqual(
            response["generation_blocked_reason"],
            "historical_hallucination_detected",
        )
        self.assertEqual(response["local_fallback_reason"], "historical_hallucination_detected")
        self.assertTrue(response["answer_grounded"])
        self.assertIn("21 de mayo de 1879", response["answer"])
        self.assertIn("Arturo Prat", response["answer"])
        self.assertIn("Esmeralda fue hundida", response["answer"])
        self.assertIn("Arturo Prat murió", response["answer"])
        for forbidden in (
            "juan manuel balmaceda",
            "monarca",
            "invadir chile",
            "bandera de victoria",
            "españoles",
            "piratas",
            "oro",
            "segunda guerra",
            "alemania",
            "italia",
            "japón",
            "misiles",
            "siglo xviii",
            "1942",
            "convoy",
            "barcos italianos",
            "navieros británicos",
        ):
            self.assertNotIn(forbidden, response["answer"].lower())

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    def test_stopped_ollama_reports_unreachable_server(self, status, _save, _settings):
        status.return_value = {
            "status": "ollama_unreachable",
            "enabled": True,
            "available": False,
            "model": "qwen3.5:2b",
            "model_installed": False,
        }
        payload = main.ChatDemoRequest(
            course="6° básico",
            subject="Automática",
            mode="Explorar mis intereses",
            question="que es un asteroide",
        )

        response = main.chat_demo(payload)

        self.assertEqual(response["ollama_status"], "ollama_unreachable")
        self.assertFalse(response["ollama_attempted"])
        self.assertIn("servidor local de Ollama está inaccesible", response["answer"])

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_verified_source_insufficient_marker_uses_safe_local_fallback(
        self, generate, status, _save, _settings
    ):
        status.return_value = {
            "enabled": True,
            "available": True,
            "model": "qwen3.5:2b",
            "model_installed": True,
        }
        generate.return_value = "FUENTE_INSUFICIENTE"

        response = main.chat_demo(self.payload())

        self.assertEqual(response["provenance_status"], "local_content_fallback")
        self.assertEqual(response["generation_blocked_reason"], "verified_source_insufficient")
        self.assertEqual(response["local_fallback_reason"], "verified_source_insufficient")
        self.assertTrue(response["answer_grounded"])
        self.assertNotIn("FUENTE_INSUFICIENTE", response["answer"])
        self.assertIn("No tengo suficiente información local verificada", response["answer"])

    @patch.object(ollama_client, "_request")
    def test_generation_disables_stream_and_thinking_and_keeps_model_loaded(self, request):
        request.return_value = {"response": "OK"}

        answer = ollama_client.generate("prueba", model="qwen3.5:2b", timeout_seconds=90)

        self.assertEqual(answer, "OK")
        payload = request.call_args.kwargs["payload"]
        self.assertFalse(payload["stream"])
        self.assertFalse(payload["think"])
        self.assertEqual(payload["keep_alive"], "10m")

    def test_ollama_error_types_have_distinct_status_codes(self):
        cases = (
            (main.OllamaUnavailableError("off"), "ollama_unreachable"),
            (main.OllamaModelNotFoundError("missing"), "model_not_installed"),
            (main.OllamaTimeoutError("slow"), "ollama_timeout"),
            (main.OllamaError("failed"), "generation_error"),
        )
        for error, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(main.ollama_error_code(error), expected)

    def test_supported_timeout_choices_and_recommended_default(self):
        self.assertEqual(main.DEFAULT_SETTINGS["ollama_timeout_seconds"], 90)
        for timeout in (40, 90, 120):
            with self.subTest(timeout=timeout):
                settings = main.validate_settings(
                    {**self.automatic_settings(), "ollama_timeout_seconds": timeout}
                )
                self.assertEqual(settings["ollama_timeout_seconds"], timeout)

    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "get_cached_ollama_status")
    def test_ai_test_preserves_preflight_timeout_status(self, status, _settings):
        status.return_value = {
            "status": "ollama_timeout",
            "enabled": True,
            "available": False,
            "model": "qwen3.5:2b",
            "model_installed": False,
        }

        response = main.run_ai_test()

        self.assertEqual(response["status"], "ollama_timeout")
        self.assertIn("excedió el tiempo máximo", response["message"])

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


    @patch.object(main, "load_settings", return_value=automatic_settings.__func__())
    @patch.object(main, "save_history", return_value=1)
    @patch.object(main, "get_ollama_status")
    @patch.object(main, "generate_with_ollama")
    def test_arturo_prat_uses_safe_local_history_answer(self, generate, status, _save, _settings):
        payload = main.ChatDemoRequest(
            course="Todos los cursos",
            subject="Automatica",
            mode="Estudiar para el colegio",
            question="quien fue Arturo Prat",
        )

        response = main.chat_demo(payload)

        self.assertEqual(response["detected_subject"], "Historia")
        self.assertEqual(response["provenance_status"], "local_verified")
        self.assertEqual(response["provider"], "local_safe")
        self.assertEqual(response["local_fallback_reason"], "grounded_history_policy")
        self.assertIn("comandada por Arturo Prat", response["answer"])
        self.assertNotIn("corbeta chilena Arturo Prat", response["answer"])
        status.assert_not_called()
        generate.assert_not_called()

    def test_iquique_validator_blocks_required_invented_claims(self):
        for invented_claim in (
            "murieron ambos comandantes",
            "ambos comandantes murieron",
            "corbeta chilena Arturo Prat",
            "Arturo Prat se vencio",
            "Bernardo O'Higgins",
            "barco chilena",
            "los chilenos fueron derrotados",
            "murio por los golpes",
            "destruyeron y hundir al navio enemigo",
            "el capitan peruano murio",
        ):
            self.assertTrue(
                main.has_iquique_historical_hallucination(
                    "explicame el combate naval de iquique", invented_claim
                )
            )

    def test_grounded_history_policy_applies_to_any_verified_history_source(self):
        self.assertTrue(
            main.should_use_grounded_history_answer(
                grounding_required=True,
                has_verified_source=True,
                subject_used="Historia",
                local_content={"subject": "Historia, Geografia y Ciencias Sociales"},
            )
        )
        self.assertTrue(
            main.should_use_grounded_history_answer(
                grounding_required=True,
                has_verified_source=True,
                subject_used="Automatica",
                local_content={"subject": "Historia, Geografia y Ciencias Sociales"},
            )
        )
        self.assertFalse(
            main.should_use_grounded_history_answer(
                grounding_required=True,
                has_verified_source=True,
                subject_used="Ciencias Naturales",
                local_content={"subject": "Ciencias Naturales"},
            )
        )

if __name__ == "__main__":
    unittest.main()
