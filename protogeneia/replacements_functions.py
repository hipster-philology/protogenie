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
            self, applies_to: List[ApplyTo]
    ):
        super(RomanNumeral, self).__init__()
        self.match_pattern: re.Regex = re.compile(match_pattern)
        self.replacement_pattern: str = replacement_pattern
        self.applies_to: List[ApplyTo] = applies_to

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

                    for apply_to in self.applies_to:
                        if self.match_pattern.search(lines[apply_to.source]):
                            for target in apply_to.target:
                                # If source and target are the same, we simply replace source by target
                                if apply_to.source == target:
                                    lines[apply_to.source] = self.match_pattern.sub(
                                        self.replacement_pattern,
                                        lines[apply_to.source]
                                    )
                                else:  # Otherwise, we just set the target value using this value
                                    lines[target] = self.replacement_pattern

                    temp.write(config.column_marker.join(list(lines.values()))+"\n")
            with open(file_path, "w") as f:
                temp.seek(0)
                f.write(temp.read())
        finally:
            temp.close()  # 5

    @classmethod
    def from_xml(cls, node: Element) -> "RomanNumeral":
        return cls(
            applies_to=[ApplyTo.from_xml(node) for node in node.findall("applyTo")]
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
