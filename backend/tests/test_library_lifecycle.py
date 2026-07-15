import unittest
from unittest.mock import patch

import content_reader
import ollama_client


class LibraryMetadataTests(unittest.TestCase):
    def test_front_matter_extracts_library_metadata_and_repairs_course_encoding(self):
        metadata = content_reader.parse_front_matter(
            '---\ntitulo: "Gravedad"\narea: "Fisica"\ncurso_origen: "2 basico"\napto_desde: "2 basico"\ntipo_contenido: "enciclopedia"\nrequiere_fuente_verificada: false\npalabras_clave:\n  - "gravedad"\n---\n# Gravedad'
        )
        self.assertEqual(metadata["topic"], "Gravedad")
        self.assertEqual(content_reader._course_number(metadata["course_origin"]), 2)
        self.assertEqual(metadata["content_type"], "enciclopedia")
        self.assertEqual(metadata["keywords"], ["gravedad"])


class OllamaLifecycleTests(unittest.TestCase):
    @patch.object(ollama_client, "_request", return_value={"done": True})
    def test_unload_uses_keep_alive_zero(self, request):
        self.assertTrue(ollama_client.unload_model(model="modelo-prueba"))
        self.assertEqual(request.call_args.kwargs["payload"]["keep_alive"], 0)

    def test_stop_does_not_touch_ollama_when_this_backend_did_not_start_it(self):
        original = ollama_client._managed_process
        try:
            ollama_client._managed_process = None
            self.assertFalse(ollama_client.stop_managed_server())
        finally:
            ollama_client._managed_process = original


if __name__ == "__main__":
    unittest.main()
