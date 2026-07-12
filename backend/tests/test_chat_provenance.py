import unittest
from unittest.mock import patch

import main


class ChatProvenanceTests(unittest.TestCase):
    def ask(self, question, course="5° básico", subject="Ciencias Naturales", mode="Estudiar para el colegio"):
        payload = main.ChatDemoRequest(
            course=course,
            subject=subject,
            mode=mode,
            question=question,
        )
        with patch.object(main, "save_history", return_value=999) as save_history:
            response = main.chat_demo(payload)
        self.assertEqual(save_history.call_args.args[0].question, question)
        return response

    def test_verified_local_source_is_presented(self):
        response = self.ask("q es habitat", course="1° básico")
        self.assertEqual(response["provenance_status"], "local_verified")
        self.assertEqual(response["provider"], "local_content")
        self.assertFalse(response["ai_context"]["ollama_enabled"])
        self.assertTrue(response["used_local_content"])
        self.assertEqual(len(response["content_sources"]), 1)
        self.assertIn("hábitat", response["content_sources"][0]["title"].lower())
        self.assertIn("Un habitat es el lugar", response["answer"])
        self.assertNotIn("Todavia no tengo una explicacion completa", response["answer"])
        self.assertEqual(response["source_course"], "1° básico")

    def test_global_verified_source_does_not_use_demo_contradiction(self):
        response = self.ask("que es la fotosintesis?", course="Todos los cursos")
        self.assertEqual(response["provenance_status"], "local_verified")
        self.assertTrue(response["used_local_content"])
        self.assertEqual(response["effective_course"], "Todos los cursos")
        self.assertEqual(response["source_course"], "6° básico")
        self.assertFalse(response["found_in_other_course"])
        self.assertNotIn("Todavia no tengo una explicacion completa", response["answer"])

    def test_school_mode_falls_back_to_verified_source_in_other_course(self):
        response = self.ask("que es la fotosintesis?", course="5° básico")
        self.assertEqual(response["provenance_status"], "local_verified")
        self.assertEqual(response["effective_course"], "5° básico")
        self.assertEqual(response["source_course"], "6° básico")
        self.assertTrue(response["found_in_other_course"])
        self.assertIn("fuente local verificada en 6° básico", response["answer"])
        self.assertNotIn("Todavia no tengo una explicacion completa", response["answer"])

    def test_external_school_topic_is_transparent_fallback(self):
        response = self.ask("me gustaria saber de tanques de la segunda guerra")
        self.assertEqual(response["provenance_status"], "no_local_content")
        self.assertFalse(response["used_local_content"])
        self.assertEqual(response["content_sources"], [])
        self.assertNotIn("Tabaco, humo y salud", response["answer"])
        self.assertIn("sin presentarla como fuente curricular", response["answer"])

    def test_external_explorer_topic_reports_missing_collection(self):
        response = self.ask(
            "me gustaria saber de tanques de la segunda guerra",
            mode="Explorar mis intereses",
        )
        self.assertEqual(response["provenance_status"], "no_local_content")
        self.assertEqual(response["content_sources"], [])
        self.assertIn("colección exploratoria local", response["answer"])

    def test_related_local_topic_is_not_presented_as_verified_source(self):
        retrieval = {
            "provenance_status": "local_related",
            "results": [],
            "related_results": [
                {
                    "title": "Océanos y lagos: luz, temperatura, presión y vida",
                    "path": "quinto_basico/ciencias_naturales/14_oceanos_y_lagos_luz_temperatura_presion_y_vida.md",
                    "section": "Conexiones con otros temas",
                    "summary": "El tema aparece como conexión con otro contenido.",
                    "excerpt": "Fotosíntesis de 6°.",
                    "score": 2,
                }
            ],
            "query_analysis": main.normalize_question("que es un habitat"),
            "minimum_score": 24,
            "best_score": 12,
        }
        with patch.object(main, "retrieve_local_content", return_value=retrieval):
            response = self.ask("que es un habitat", course="1° básico")

        self.assertEqual(response["provenance_status"], "local_related")
        self.assertEqual(response["provider"], "demo")
        self.assertFalse(response["used_local_content"])
        self.assertEqual(response["content_sources"], [])
        self.assertTrue(response["related_sources"])
        self.assertIn("relación cercana", response["answer"])

    def test_ambiguous_follow_up_requests_clarification(self):
        response = self.ask("cual fue el mas usado?")
        self.assertEqual(response["provenance_status"], "clarification_required")
        self.assertFalse(response["used_local_content"])
        self.assertEqual(response["content_sources"], [])
        self.assertIn("¿Puedes decirme a qué tema", response["answer"])


if __name__ == "__main__":
    unittest.main()
