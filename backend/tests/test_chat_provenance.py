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
        self.assertTrue(response["used_local_content"])
        self.assertEqual(len(response["content_sources"]), 1)
        self.assertIn("hábitat", response["content_sources"][0]["title"].lower())
        self.assertIn("Un habitat es el lugar", response["answer"])

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

    def test_ambiguous_follow_up_requests_clarification(self):
        response = self.ask("cual fue el mas usado?")
        self.assertEqual(response["provenance_status"], "clarification_required")
        self.assertFalse(response["used_local_content"])
        self.assertEqual(response["content_sources"], [])
        self.assertIn("¿Puedes decirme a qué tema", response["answer"])


if __name__ == "__main__":
    unittest.main()
