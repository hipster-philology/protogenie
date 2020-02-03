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

