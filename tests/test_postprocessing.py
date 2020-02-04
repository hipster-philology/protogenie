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
