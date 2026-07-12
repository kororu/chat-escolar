import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import main


class ConversationContextIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_db_path = main.DB_PATH
        main.DB_PATH = Path(self.temporary_directory.name) / "chat_escolar_test.db"
        main.init_db()
        self.client = TestClient(main.app)
        self.erik = self.create_profile("Erik")
        self.ariel = self.create_profile("Ariel")

    def tearDown(self):
        main.DB_PATH = self.original_db_path
        self.temporary_directory.cleanup()

    def create_profile(self, name):
        response = self.client.post(
            "/profiles",
            json={"name": name, "role": "Estudiante", "course": "5° básico"},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()["profile"]

    def ask(
        self,
        profile,
        question,
        conversation_id="conversation-test",
        course=None,
        mode="Explorar mis intereses",
    ):
        response = self.client.post(
            "/chat/demo",
            json={
                "profile_id": profile["id"],
                "conversation_id": conversation_id,
                "course": course or profile["course"],
                "subject": "Ciencias Naturales",
                "mode": mode,
                "question": question,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_follow_up_rebuilds_tanks_question_for_same_profile(self):
        self.ask(self.erik, "me gustaria saber de tanques de la segunda guerra")
        follow_up = self.ask(self.erik, "cual fue el mas usado?")

        context = follow_up["conversation_context"]
        self.assertTrue(context["used_context"])
        self.assertGreaterEqual(context["confidence"], 0.8)
        self.assertEqual(
            context["contextual_question"],
            "cual fue el tanque mas usado durante la segunda guerra mundial",
        )
        self.assertEqual(context["active_topic"], "tanques durante la Segunda Guerra Mundial")

        connection = sqlite3.connect(main.DB_PATH)
        try:
            stored = connection.execute(
                """
                SELECT question, normalized_question, contextual_question, conversation_id,
                       active_topic, context_confidence
                FROM chat_history
                WHERE profile_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (self.erik["id"],),
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(stored[0], "cual fue el mas usado?")
        self.assertEqual(stored[2], context["contextual_question"])
        self.assertEqual(stored[3], "conversation-test")

    def test_clear_topic_change_does_not_inherit_tanks(self):
        self.ask(self.erik, "me gustaria saber de tanques de la segunda guerra")
        habitat = self.ask(self.erik, "que es un habitat")

        context = habitat["conversation_context"]
        self.assertFalse(context["used_context"])
        self.assertEqual(context["contextual_question"], "que es un habitat")
        self.assertEqual(context["active_topic"], "habitat")
        self.assertNotIn("tanque", context["contextual_question"])

    def test_another_example_uses_ecosystem_topic(self):
        self.ask(self.erik, "que es un ecosistema")
        follow_up = self.ask(self.erik, "dame otro ejemplo")

        context = follow_up["conversation_context"]
        self.assertTrue(context["used_context"])
        self.assertEqual(context["active_topic"], "ecosistema")
        self.assertEqual(context["contextual_question"], "dame otro ejemplo de ecosistema")

    def test_profiles_never_share_conversation_context(self):
        self.ask(self.erik, "me gustaria saber de tanques de la segunda guerra", "shared-id")
        ariel_follow_up = self.ask(self.ariel, "cual fue el mas usado?", "shared-id")

        context = ariel_follow_up["conversation_context"]
        self.assertFalse(context["used_context"])
        self.assertEqual(ariel_follow_up["provenance_status"], "clarification_required")
        self.assertNotIn("tanque", ariel_follow_up["answer"].lower())

    def test_incomplete_question_without_context_requests_clarification(self):
        response = self.ask(self.erik, "cual fue el mas usado?")
        self.assertEqual(response["provenance_status"], "clarification_required")
        self.assertFalse(response["conversation_context"]["used_context"])
        self.assertIn("¿Puedes decirme a qué tema", response["answer"])

    def test_active_course_from_frontend_overrides_profile_course_for_search(self):
        response = self.ask(
            self.erik,
            "que es la fotosintesis?",
            course="6° básico",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(self.erik["course"], "5° básico")
        self.assertEqual(response["active_course"], "6° básico")
        self.assertEqual(response["profile_course"], "5° básico")
        self.assertEqual(response["effective_course"], "6° básico")
        self.assertEqual(response["source_course"], "6° básico")
        self.assertEqual(response["provenance_status"], "local_verified")
        self.assertFalse(response["found_in_other_course"])


if __name__ == "__main__":
    unittest.main()
