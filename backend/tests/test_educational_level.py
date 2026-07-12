import unittest

from educational_level import get_educational_level


class EducationalLevelTests(unittest.TestCase):
    def test_first_grade_uses_short_initial_level(self):
        level = get_educational_level("1° básico")
        self.assertEqual(level["approx_age"], "6 a 7 años")
        self.assertEqual(level["max_words"], 90)
        self.assertEqual(level["practice_questions"], 1)

    def test_fifth_grade_uses_intermediate_school_level(self):
        level = get_educational_level("5° básico")
        self.assertEqual(level["approx_age"], "10 a 11 años")
        self.assertEqual(level["max_main_ideas"], 3)
        self.assertEqual(level["max_words"], 170)

    def test_eighth_grade_allows_more_precise_depth(self):
        level = get_educational_level("8° básico")
        self.assertEqual(level["approx_age"], "13 a 14 años")
        self.assertEqual(level["max_words"], 220)


if __name__ == "__main__":
    unittest.main()
