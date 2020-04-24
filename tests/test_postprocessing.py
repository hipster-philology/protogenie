from .helpers import _TestHelper


class TestPostProcessing(_TestHelper):
    def test_disambiguation(self):
        self._dispatch(
            output_dir="./tests/tests_output/",
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/disambiguation.xml"
        )
        tokens = 0
        for line in self.read_file("train", "disambiguation.tsv"):
            if line:  # Some line can be empty
                self.assertFalse(line["lemma"][-1].isnumeric(), "Last number should not be numeric")
                self.assertTrue(line["lemma-disambiguation-index"].isnumeric(), "Disambiguation should be numeric")
                tokens += 1
        self.assertEqual(tokens, 150*0.8, "There should be 150 * 80% tokens")

    def test_replace(self):
        """ Ensure that replacement would work """
        self._dispatch(
            output_dir="./tests/tests_output/",

            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/replacement.xml"
        )
        # Checking all corpora just to be sure
        tokens = 0
        numbers = 0
        number_founds = []

        for line in self.read_file("train", "replacement.tsv"):
            if line:  # Some line can be empty
                if line["form"].isnumeric():
                    self.assertEqual(line["lemma"], line["form"], "Lemma and token should be equal")
                    if line["lemma"] == "3" and line["POS"] != "3":
                        # If we have a 3, and 3 was not the original,
                        #   we should have something else in POS (which mirrored lemma and token)
                        self.assertNotEqual(line["lemma"], line["POS"], "Lemma and POS should differ, "
                                                                        "except if they are 1 and 3")
                    elif line["POS"] in ["0", "1"]:
                        self.assertEqual(line["lemma"], "1")
                        self.assertEqual(line["form"], "1")
                    else:  # We have three and it shoud equal
                        self.assertEqual(line["lemma"], line["POS"], "Lemma and POS should be the same for 3 and 1")

                    number_founds.append(line["lemma"])
                    numbers += 1
                tokens += 1

        for line in self.read_file("dev", "replacement.tsv"):
            if line:  # Some line can be empty
                if line["form"].isnumeric():
                    self.assertEqual(line["lemma"], line["form"], "Lemma and token should be equal")
                    number_founds.append(line["lemma"])
                    numbers += 1
                tokens += 1

        for line in self.read_file("test", "replacement.tsv"):
            if line:  # Some line can be empty
                if line["form"].isnumeric():
                    self.assertEqual(line["lemma"], line["form"], "Lemma and token should be equal")
                    number_founds.append(line["lemma"])
                    numbers += 1
                tokens += 1

        self.assertEqual(tokens, 140, "There should be 140 tokens")
        self.assertEqual(len(number_founds), 140/7, "There should be one number each 7 chars")
        self.assertEqual(sorted(list(set(number_founds))), ["1", "3"], "There should be only two different numbers")

    def test_skip(self):
        """ Ensure that replacement would work """
        self._dispatch(
            output_dir="./tests/tests_output/",

            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/skip.xml"
        )

        # Checking all corpora just to be sure
        tokens = 0

        for line in self.read_file("train", "skip.tsv"):
            if line:  # Some line can be empty
                self.assertNotEqual(line["form"], ".", "There should not be a single dot in token")
                self.assertNotEqual(line["POS"], "PUNfrt", "There should not be a single dot in token")
                tokens += 1

        self.assertEqual(tokens, 200*0.8*0.8,
                         "There should be 80% of total tokens - 20% (1 of 5 char is a dot) that were removed")

    def test_roman_numbers(self):
        """ Check roman numbers validity """
        _, config = self._dispatch(
            output_dir="./tests/tests_output/",
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/roman_numbers.xml"
        )

        # Checking all corpora just to be sure
        tokens = 0
        romnums = 0
        for line in self.read_file("train", "roman_numbers.tsv"):
            if line:  # Some line can be empty
                if line["POS"] == "RomNum":
                    romnums += 1
                    self.assertTrue(line["form"].isnumeric(), "RomanNumeral should have been converted to int")
                    self.assertTrue(line["lemma"].isnumeric(), "RomanNumeral should have been converted to int")
                tokens += 1

        self.assertEqual(tokens, 300*0.8,
                         "There should be 80% of total tokens")
        self.assertEqual(romnums, 300*0.8*0.2,
                         "There should be 20% of the train corpus that were numerals")

    def test_clitics(self):
        """ Check that clitics are dealt with correctly"""
        _, config = self._dispatch(
            output_dir="./tests/tests_output/",
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/clitics.xml"
        )
        # Checking all corpora just to be sure
        tokens = 0
        clitics = 0

        for line in self.read_file("train", "clitics.tsv"):
            if line:  # Some line can be empty
                if "界" in line["lemma"]:
                    clitics += 1
                    self.assertTrue(line["token"].endswith("ne"), "Clitic has been passed to token")
                    self.assertTrue(line["lemma"].endswith("界ne"), "Clitic has been passed to lemma with glue")
                    self.assertFalse(line["token"].endswith("界ne"), "Clitic has been passed to token without glue")
                tokens += 1
                print(line)

        print(tokens)
        self.assertEqual(tokens, 300*0.8 * 0.8,
                         "There should be 80% of total tokens, and 20% of that should have been removed (2 clitics"
                         "every 10 words)")
        self.assertEqual(clitics, 300*0.8*0.2, "There should be 2 clitics for 8 words")
