import unittest
from unittest.mock import patch

from content_reader import (
    detect_subject_from_question,
    normalize_text,
    normalize_question,
    reload_local_content_index,
    retrieve_local_content,
)


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

    def test_retrieval_does_not_decide_conversational_ambiguity(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "cual fue el mas usado?",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "no_local_content")
        self.assertEqual(result["results"], [])

    def test_consiste_is_not_corrected_to_ecosistemas(self):
        analysis = normalize_question(
            "explicame en que consiste el combate naval de iquique"
        )
        self.assertEqual(
            analysis["normalized_text"],
            "explicame en que consiste el combate naval de iquique",
        )
        self.assertIsNone(analysis["possible_topic"])
        self.assertNotIn("ecosistemas", analysis["keywords"])

    def test_detects_curricular_subjects_from_normalized_questions(self):
        examples = {
            "Que es la fotosintesis?": "Ciencias Naturales",
            "explicame las fracciones": "Matemática",
            "quien fue Arturo Prat": "Historia",
            "que es un sustantivo": "Lenguaje",
        }
        for question, expected_subject in examples.items():
            with self.subTest(question=question):
                subject, confidence = detect_subject_from_question(question)
                self.assertEqual(subject, expected_subject)
                self.assertGreaterEqual(confidence, 0.6)

    def test_historical_naval_phrases_have_priority_over_other_subjects(self):
        for question in (
            "explicame el combate naval de iquique",
            "quien fue Arturo Prat",
            "que paso el 21 de mayo",
            "guerra del pacífico",
            "Esmeralda",
            "Huáscar",
            "Miguel Grau",
        ):
            with self.subTest(question=question):
                subject, confidence = detect_subject_from_question(question)
                self.assertEqual(subject, "Historia")
                self.assertEqual(confidence, 1.0)

    def test_historical_naval_queries_recover_the_verified_history_source(self):
        for question in (
            "explicame en que consiste el combate naval de iquique",
            "quien fue Arturo Prat",
            "que paso el 21 de mayo",
            "Esmeralda",
            "Huáscar",
            "Miguel Grau",
        ):
            with self.subTest(question=question):
                result = retrieve_local_content(
                    "Todos los cursos",
                    "Historia",
                    question,
                    mode="Estudiar para el colegio",
                )
                self.assertEqual(result["provenance_status"], "local_verified")
                self.assertEqual(result["results"][0]["title"], "Combate Naval de Iquique")
                self.assertEqual(result["source_course"], "6° básico")

    def test_ambiguous_question_does_not_invent_subject(self):
        subject, confidence = detect_subject_from_question("explícame esto mejor")
        self.assertIsNone(subject)
        self.assertEqual(confidence, 0.0)


class ContentRelevanceTests(unittest.TestCase):
    def test_retrieval_reuses_the_loaded_content_index(self):
        self.assertGreater(reload_local_content_index(), 0)

        with patch("pathlib.Path.read_text", side_effect=AssertionError("El índice no debe releer archivos")):
            result = retrieve_local_content(
                "6° básico",
                "Ciencias Naturales",
                "que es la fotosintesis",
                mode="Estudiar para el colegio",
            )

        self.assertEqual(result["provenance_status"], "local_verified")

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
        self.assertTrue(first["matched_terms"])
        self.assertTrue(first["is_exact_match"])
        self.assertEqual(result["confidence"], "high")
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
        self.assertEqual(result["provenance_status"], "local_related")
        self.assertEqual(result["results"], [])
        self.assertEqual(result["query_analysis"]["possible_topic"], "habitat")

    def test_low_confidence_is_separate_from_related_topic(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "energia",
            mode="Estudiar para el colegio",
            minimum_score=999,
        )
        self.assertEqual(result["provenance_status"], "local_low_confidence")
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["query_analysis"]["possible_topic"])

    def test_without_candidates_reports_no_local_content(self):
        result = retrieve_local_content(
            "1° básico",
            "Ciencias Naturales",
            "casa",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "no_local_content")
        self.assertEqual(result["best_score"], 0)
        self.assertEqual(result["results"], [])

    def test_fifth_grade_photosynthesis_is_related_not_verified(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "que es la fotosintesis?",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "local_related")
        self.assertEqual(result["results"], [])
        self.assertTrue(result["related_results"])
        self.assertEqual(result["confidence"], "related")
        self.assertIn("relación", result["reason"])
        related_title = normalize_text(result["related_results"][0]["title"])
        self.assertIn("oceanos", related_title)
        self.assertNotIn("respiratorio", related_title)
        self.assertTrue(result["related_results"][0]["section"])
        self.assertTrue(result["related_results"][0]["summary"])

    def test_sixth_grade_photosynthesis_can_use_direct_source(self):
        result = retrieve_local_content(
            "6° básico",
            "Ciencias Naturales",
            "fotosíntesis de 6°",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "local_verified")
        self.assertTrue(result["results"])
        self.assertIn("fotosintesis", normalize_text(result["results"][0]["title"]))
        self.assertEqual(result["source_course"], "6° básico")
        self.assertFalse(result["found_in_other_course"])

    def test_global_search_can_find_photosynthesis_source(self):
        result = retrieve_local_content(
            "Todos los cursos",
            "Ciencias Naturales",
            "que es la fotosintesis?",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "local_verified")
        self.assertEqual(result["effective_course"], "Todos los cursos")
        self.assertEqual(result["source_course"], "6° básico")
        self.assertFalse(result["found_in_other_course"])
        self.assertIn("fotosintesis", normalize_text(result["results"][0]["title"]))

    def test_explorer_mode_searches_global_local_content_before_fallback(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "que es la fotosintesis?",
            mode="Explorar mis intereses",
        )
        self.assertEqual(result["provenance_status"], "local_verified")
        self.assertEqual(result["effective_course"], "5° básico")
        self.assertEqual(result["source_course"], "6° básico")
        self.assertTrue(result["found_in_other_course"])
        self.assertIn("fotosintesis", normalize_text(result["results"][0]["title"]))

    def test_respiratory_system_still_uses_direct_source(self):
        result = retrieve_local_content(
            "5° básico",
            "Ciencias Naturales",
            "que es sistema respiratorio",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "local_verified")
        self.assertTrue(result["results"])
        self.assertIn("sistema respiratorio", normalize_text(result["results"][0]["title"]))

    def test_eighth_grade_linear_equations_use_direct_math_source(self):
        result = retrieve_local_content(
            "8° básico",
            "Matemática",
            "que es una ecuacion lineal",
            mode="Estudiar para el colegio",
        )
        self.assertEqual(result["provenance_status"], "local_verified")
        self.assertEqual(result["source_course"], "8° básico")
        self.assertIn("ecuaciones lineales", normalize_text(result["results"][0]["title"]))

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
