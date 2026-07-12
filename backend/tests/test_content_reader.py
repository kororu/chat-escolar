import unittest

from content_reader import normalize_text, normalize_question, retrieve_local_content


class QuestionNormalizationTests(unittest.TestCase):
    HABITAT_VARIANTS = (
        "q es habitat",
        "que es un habitat?",
        "¿q es un havitat?",
        "¿que es un habitat",
        "k es habitat",
        "ke es un abitad",
    )

    def test_habitat_variants_share_canonical_analysis(self):
        for question in self.HABITAT_VARIANTS:
            with self.subTest(question=question):
                analysis = normalize_question(question)
                self.assertEqual(analysis["original_text"], question)
                self.assertEqual(analysis["normalized_text"], "que es un habitat")
                self.assertEqual(analysis["intent"], "definition")
                self.assertEqual(analysis["possible_topic"], "habitat")
                self.assertEqual(analysis["possible_subject"], "ciencias_naturales")
                self.assertIn("habitat", analysis["keywords"])

    def test_vague_follow_up_requires_clarification(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "cual fue el mas usado?",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "clarification_required")
        self.assertEqual(result["results"], [])


class ContentRelevanceTests(unittest.TestCase):
    def test_tanks_never_recover_curricular_science_sources(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "me gustaria saber de tanques de la segunda guerra",
            mode="Estudiar para el colegio",
        )
        titles = " ".join(item["title"] for item in result["results"])
        self.assertEqual(result["provenance_status"], "no_local_content")
        self.assertEqual(result["results"], [])
        for forbidden in ("tabaco", "circuitos", "energia electrica", "distribucion de agua"):
            self.assertNotIn(forbidden, normalize_text(titles))

    def test_habitat_prioritizes_relevant_life_science_content(self):
        result = retrieve_local_content(
            "1° básico",
            "Ciencias Naturales",
            "ke es un abitad",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "local_verified")
        self.assertTrue(result["results"])
        first = result["results"][0]
        self.assertIn("habitat", normalize_text(first["title"]))
        self.assertLessEqual(len(first["excerpt"]), 800)
        self.assertTrue(first["excerpt"].endswith((".", "?", "!", "…")))

    def test_below_threshold_is_not_verified(self):
        result = retrieve_local_content(
            "1° básico",
            "Ciencias Naturales",
            "que es un habitat",
            mode="Estudiar para el colegio",
            minimum_score=999,
        )
        self.assertEqual(result["provenance_status"], "local_low_confidence")
        self.assertEqual(result["results"], [])

    def test_explorer_without_collection_does_not_search_curriculum(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "me gustaria saber de tanques de la segunda guerra",
            mode="Explorar mis intereses",
        )
        self.assertEqual(result["provenance_status"], "no_local_content")
        self.assertEqual(result["results"], [])


if __name__ == "__main__":
    unittest.main()

