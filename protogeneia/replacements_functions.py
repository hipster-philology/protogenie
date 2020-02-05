if False:
    from .configs import CorpusConfiguration
import tempfile
import regex as re
from xml.etree.ElementTree import Element
import csv
from typing import List
from .postprocessing import ApplyTo, PostProcessing


class RomanNumeral(PostProcessing):
    NODE = "utils"

    def __init__(
            self, apply_to: ApplyTo
    ):
        """ Transform Roman Numerals to Integers

        :param apply_to: List of fields that should have the rules applied to
        """
        super(RomanNumeral, self).__init__()
        # Just thank you, dear anonymous hero named Corin
        # User: https://stackoverflow.com/users/302306/corin
        # Source: https://stackoverflow.com/a/10441405
        self.match_pattern: re.Regex = re.compile(r"(M{1,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})|M{0,4}"
                                                  r"(CM|C?D|D?C{1,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})|M{0,4}"
                                                  r"(CM|CD|D?C{0,3})(XC|X?L|L?X{1,3})(IX|IV|V?I{0,3})|M{0,4}"
                                                  r"(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|I?V|V?I{1,3}))")
        self.apply_to: ApplyTo = apply_to

    def apply(self, file_path: str, config: "CorpusConfiguration"):
        temp = tempfile.TemporaryFile(mode="w+")  # 2

        try:
            with open(file_path) as file:
                csv_reader = csv.reader(file, delimiter=config.column_marker)
                header: List[str] = []
                for nb_line, line in enumerate(csv_reader):  # The file should already have been open
                    if nb_line == 0:
                        temp.write(config.column_marker.join(line)+"\n")
                        header = line
                        continue
                    elif not line:
                        temp.write("\n")
                        continue
                    lines = dict(zip(header, line))

                    if self.match_pattern.search(lines[self.apply_to.source]):
                        original = {k: v for k, v in original.items()}
                        result = self.from_roman(original[self.apply_to.source])

                        for target in self.apply_to.target:
                            # If source and target are the same, we simply replace source by target
                            if self.apply_to.source == target:
                                lines[self.apply_to.source] = result
                            else:  # Otherwise, we just copy the result value to the target
                                lines[target] = result

                    temp.write(config.column_marker.join(list(lines.values()))+"\n")
            with open(file_path, "w") as f:
                temp.seek(0)
                f.write(temp.read())
        finally:
            temp.close()  # 5

    @classmethod
    def from_xml(cls, node: Element) -> "RomanNumeral":
        return cls(
            apply_to=ApplyTo.from_xml(node.find("applyTo"))
        )

    @staticmethod
    def from_roman(num: str) -> int:
        """

        Source: https://stackoverflow.com/questions/19308177/converting-roman-numerals-to-integers-in-python
        Author: https://stackoverflow.com/users/1201737/r366y
        :param num:
        :return:
        """
        roman_numerals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        result = 0
        for i,c in enumerate(num.upper()):
            if (i+1) == len(num) or roman_numerals[c] >= roman_numerals[num[i+1]]:
                result += roman_numerals[c]
            else:
                result -= roman_numerals[c]
        return result

    @classmethod
    def match_config_node(cls, node: Element) -> bool:
        return node.tag == cls.NodeName and node.get("function", "RomanNumerals")
