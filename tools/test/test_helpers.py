
import conwrap.helpers as helpers
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
        hint_dir = os.path.join(dir_path, "stubs", "recipe")
        r_path = helpers.guess_recipe_dir("package/1.2.3@", hint_dir)
        self.assertIsNotNone(r_path)
        self.assertEqual(
            os.path.basename(
                os.path.dirname(r_path)),
                "recipe")
        r_path = helpers.guess_recipe_dir("package/1.2.3@", "no/where/here")
        self.assertIsNone(r_path)

    def test_recipe_dir_env(self):
        dir_path = os.path.dirname(__file__)
        hint_dir = os.path.join(dir_path, "stubs", "recipe")
        os.environ["CONAN_RECIPE_DIRS"] = hint_dir
        r_path = helpers.guess_recipe_dir("package/1.2.3@")
        self.assertIsNotNone(r_path)
        self.assertEqual(
            os.path.basename(
                os.path.dirname(r_path)),
                "recipe")
        os.environ["CONAN_RECIPE_DIRS"] = "/no/where/here:"
        r_path = helpers.guess_recipe_dir("package/1.2.3@")
        self.assertIsNone(r_path)

    def test_recipe_dir_in_here(self):
        r_path = helpers.guess_recipe_dir("zlib/1.2.11@")
        self.assertIsNotNone(r_path)
        self.assertIsNone(helpers.guess_recipe_dir("zlibss/1.2.11@"))


class TestGetConanFile(unittest.TestCase):

    def test_just_a_file(self):
        # assume alljoyn stays as it is, just a simple dir
        reference = "alljoyn/0.16.10@"
        conan_file = helpers.get_conan_file(reference)
        self.assertIsNotNone(conan_file)
        self.assertTrue(os.path.exists(conan_file), f"Not a path: {conan_file}")

    def test_not_a_dir(self):
        self.assertIsNone(helpers.get_conan_file("all__joyn/0.16.10@"))

    def test_cci(self):
        reference = "sol2/3.2.2@"
        conan_file = helpers.get_conan_file(reference)
        self.assertIsNotNone(conan_file)
        self.assertTrue(os.path.exists(conan_file), f"Not a path: {conan_file}")

    def test_cci_but_wrong_version(self):
        reference = "zlib/1.2.10@"
        conan_file = helpers.get_conan_file(reference)
        self.assertIsNone(conan_file)

    def test_edge_cases(self):
        dir_path = os.path.dirname(__file__)
        hint_dir = os.path.join(dir_path, "stubs", "recipe")
        os.environ["CONAN_RECIPE_DIRS"] = hint_dir
        reference = "package/1.2.3@"
        self.assertIsNotNone(helpers.get_conan_file(reference))
        reference = "package/1.2.2@"
        self.assertIsNone(helpers.get_conan_file(reference))


class TestSpecParsing(unittest.TestCase):

    def test_a_simple_list(self):
        args = helpers.parse_spec("A,B,C")
        self.assertListEqual(args, ["A","B","C"])

    def test_a_simple_list_with_filter(self):
        args = helpers.parse_spec("A,B,C, , #D")
        self.assertListEqual(args, ["A","B","C"])

    def test_a_list_from_file(self):
        dir_path = os.path.dirname(__file__)
        file_path = os.path.join(dir_path, "stubs", "speclist.txt")
        args = helpers.parse_spec(file_path)
        self.assertListEqual(args, ["A","B","D"])

if __name__ == '__main__':
    unittest.main()
