from .helpers import _TestHelper
from tempfile import TemporaryDirectory
import os.path as p
import filecmp
import subprocess
import sys

import os

is_ci = os.getenv("CI", False) != False
PATH = os.getenv("PATH")


class TestCli(_TestHelper):
    def subprocess(self, *args, **kwargs):
        if not is_ci:
            kwargs.update({"env": {"PATH": os.getenv("PATH")}})
        return subprocess.run(*args, **kwargs)

    def test_get_scheme(self):
        """ Test that we are able to get current version scheme """
        with TemporaryDirectory(dir="./") as cur_dir:
            dest = p.join(cur_dir, "scheme.rng")
            _ = self.subprocess(["protogenie", "get-scheme",  dest])
            self.assertTrue(
                filecmp.cmp("./protogenie/schema.rng", dest),
                "Copied scheme should be the same one from the package"
            )
