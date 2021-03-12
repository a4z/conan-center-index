
import tools.helpers as helpers
import unittest
import os


class TestReferenceHelpers(unittest.TestCase):

    valid_ref1 = "package/1.2.3@"
    valid_ref2 = "package/1.2.3@user/channel"
    invalid_refs = ["package0/1.2.3",
                    "package1.2.3@user/channe.",
                    "package2/1.2.3@user/",
                    "package3/1.2.3@user",
                    "package4/1.2.3@/",
                    "/1.2.3@",
                    "package5/@",
                    ]

    def test_name_validation(self):
        self.assertTrue(helpers.is_reference_name(self.valid_ref1))
        self.assertTrue(helpers.is_reference_name(self.valid_ref2))
        for ref in self.invalid_refs:
            self.assertFalse(helpers.is_reference_name(ref))

    def test_name(self):
        self.assertEqual(helpers.reference_name(self.valid_ref1), "package")
        self.assertEqual(helpers.reference_name(self.valid_ref2), "package")
        for ref in self.invalid_refs:
            self.assertIsNone(helpers.reference_name(ref))

    def test_version(self):
        self.assertEqual(helpers.reference_version(self.valid_ref1), "1.2.3")
        self.assertEqual(helpers.reference_version(self.valid_ref2), "1.2.3")
        for ref in self.invalid_refs:
            self.assertIsNone(helpers.reference_version(ref))


class TestGuessRecipeDir(unittest.TestCase):

    def test_recipe_dir_hint(self):
        dir_path = os.path.dirname(__file__)
        hint_dir = os.path.join(dir_path, "mock_recipe")
        r_path = helpers.guess_recipe_dir("package/1.2.3@", hint_dir)
        self.assertIsNotNone(r_path)
        self.assertEqual(
            os.path.basename(
                os.path.dirname(r_path)),
            "mock_recipe")
        r_path = helpers.guess_recipe_dir("package/1.2.3@", "no/where/here")
        self.assertIsNone(r_path)

    def test_recipe_dir_env(self):
        dir_path = os.path.dirname(__file__)
        hint_dir = os.path.join(dir_path, "mock_recipe")
        os.environ["CONAN_RECIPE_DIRS"] = hint_dir
        r_path = helpers.guess_recipe_dir("package/1.2.3@")
        self.assertIsNotNone(r_path)
        self.assertEqual(
            os.path.basename(
                os.path.dirname(r_path)),
            "mock_recipe")
        os.environ["CONAN_RECIPE_DIRS"] = "/no/where/here:"
        r_path = helpers.guess_recipe_dir("package/1.2.3@")
        self.assertIsNone(r_path)

    def test_recipe_dir_in_here(self):
        r_path = helpers.guess_recipe_dir("zlib/1.2.11@")
        self.assertIsNotNone(r_path)
        self.assertIsNone(helpers.guess_recipe_dir("zlibss/1.2.11@"))

if __name__ == '__main__':
    unittest.main()
