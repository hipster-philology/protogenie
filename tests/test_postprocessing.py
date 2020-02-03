from .helpers import _TestHelper


class TestPostProcessing(_TestHelper):
    def test_disambiguation(self):
        self._dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
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
