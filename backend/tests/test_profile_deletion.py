import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class ProfileDeletionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_db_path = main.DB_PATH
        self.original_avatar_directory = main.AVATAR_DIRECTORY
        main.DB_PATH = Path(self.temporary_directory.name) / "chat_escolar_test.db"
        main.AVATAR_DIRECTORY = Path(self.temporary_directory.name) / "profile_avatars"
        main.init_db()
        self.client = TestClient(main.app)
        self.ollama_status = patch.object(
            main,
            "get_cached_ollama_status",
            return_value={"enabled": True, "available": False, "model": "qwen3.5:2b", "model_installed": False},
        )
        self.ollama_status.start()

    def tearDown(self):
        self.ollama_status.stop()
        main.DB_PATH = self.original_db_path
        main.AVATAR_DIRECTORY = self.original_avatar_directory
        self.temporary_directory.cleanup()

    def create_profile(self, name):
        response = self.client.post(
            "/profiles",
            json={"name": name, "role": "Estudiante", "course": "5° básico"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["profile"]

    def create_history(self, profile):
        response = self.client.post(
            "/chat/demo",
            json={
                "profile_id": profile["id"],
                "conversation_id": f"conversation-{profile['id']}",
                "course": profile["course"],
                "subject": "Ciencias Naturales",
                "mode": "Estudiar para el colegio",
                "question": "que es un habitat",
            },
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_confirmed_deletion_removes_unicode_profile_and_its_history_only(self):
        unicode_profile = self.create_profile("Arieñ")
        other_profile = self.create_profile("Erik")
        self.create_history(unicode_profile)
        self.create_history(other_profile)

        response = self.client.delete(f"/profiles/{unicode_profile['id']}")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["deleted_profile"], {"id": unicode_profile["id"], "name": "Arieñ"})
        self.assertEqual(body["deleted_history_count"], 1)

        profiles = self.client.get("/profiles").json()["items"]
        self.assertEqual([profile["id"] for profile in profiles], [other_profile["id"]])
        self.assertEqual(self.client.get(f"/profiles/{unicode_profile['id']}").status_code, 404)

        deleted_history = self.client.get(
            "/history", params={"profile_id": unicode_profile["id"]}
        ).json()["items"]
        other_history = self.client.get(
            "/history", params={"profile_id": other_profile["id"]}
        ).json()["items"]
        self.assertEqual(deleted_history, [])
        self.assertEqual(len(other_history), 1)
        self.assertEqual(other_history[0]["profile_id"], other_profile["id"])

    def test_cancel_path_keeps_profile_and_history_unchanged_without_delete_request(self):
        profile = self.create_profile("Ariel")
        self.create_history(profile)

        # Cancelar en la interfaz no llama DELETE; el estado del backend queda intacto.
        self.assertEqual(self.client.get(f"/profiles/{profile['id']}").status_code, 200)
        history = self.client.get("/history", params={"profile_id": profile["id"]}).json()["items"]
        self.assertEqual(len(history), 1)

    def test_nonexistent_id_returns_clear_not_found_response(self):
        response = self.client.delete("/profiles/999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Perfil no encontrado")

    def test_deleting_last_profile_leaves_empty_profile_list(self):
        profile = self.create_profile("Erik")
        response = self.client.delete(f"/profiles/{profile['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/profiles").json()["items"], [])

    def upload_avatar(self, profile, content=b"\x89PNG\r\n\x1a\navatar", content_type="image/png", filename="avatar.png"):
        return self.client.post(
            f"/profiles/{profile['id']}/avatar",
            content=content,
            headers={"content-type": content_type, "x-avatar-filename": filename},
        )

    def test_avatar_is_local_and_can_be_removed_without_affecting_another_profile(self):
        first_profile = self.create_profile("Ariel")
        second_profile = self.create_profile("Erik")
        upload = self.upload_avatar(first_profile)
        self.assertEqual(upload.status_code, 200, upload.text)
        self.assertEqual(upload.json()["profile"]["avatar_url"], f"/profiles/{first_profile['id']}/avatar")

        avatar = self.client.get(f"/profiles/{first_profile['id']}/avatar")
        self.assertEqual(avatar.status_code, 200)
        self.assertEqual(avatar.headers["content-type"], "image/png")
        self.assertEqual(avatar.content, b"\x89PNG\r\n\x1a\navatar")

        self.assertIsNone(self.client.get(f"/profiles/{second_profile['id']}").json()["profile"]["avatar_url"])
        deleted = self.client.delete(f"/profiles/{first_profile['id']}/avatar")
        self.assertEqual(deleted.status_code, 200)
        self.assertIsNone(deleted.json()["profile"]["avatar_url"])
        self.assertEqual(self.client.get(f"/profiles/{first_profile['id']}/avatar").status_code, 404)

    def test_avatar_validation_rejects_unsupported_and_oversized_files(self):
        profile = self.create_profile("Arieñ")
        invalid = self.upload_avatar(profile, content_type="text/plain", filename="avatar.txt")
        self.assertEqual(invalid.status_code, 415)

        oversized = self.upload_avatar(
            profile,
            content=b"x" * (main.MAX_AVATAR_SIZE_BYTES + 1),
        )
        self.assertEqual(oversized.status_code, 413)
        self.assertIsNone(self.client.get(f"/profiles/{profile['id']}").json()["profile"]["avatar_url"])

    def test_deleting_profile_removes_only_its_avatar_file(self):
        first_profile = self.create_profile("Arieñ")
        second_profile = self.create_profile("Erik")
        self.assertEqual(self.upload_avatar(first_profile).status_code, 200)
        self.assertEqual(self.upload_avatar(second_profile, content=b"\x89PNG\r\n\x1a\nsecond").status_code, 200)

        self.assertEqual(self.client.delete(f"/profiles/{first_profile['id']}").status_code, 200)
        self.assertEqual(self.client.get(f"/profiles/{first_profile['id']}/avatar").status_code, 404)
        remaining = self.client.get(f"/profiles/{second_profile['id']}/avatar")
        self.assertEqual(remaining.status_code, 200)
        self.assertEqual(remaining.content, b"\x89PNG\r\n\x1a\nsecond")


if __name__ == "__main__":
    unittest.main()
