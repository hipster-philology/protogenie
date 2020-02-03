if False:
    from .configs import CorpusConfiguration
import tempfile
import regex as re
from xml.etree.ElementTree import Element
import csv
from typing import List


class Disambiguation(object):
    def __init__(self, lemma_key: str, disambiguation_key: str, match_pattern: str):
        self.lemma_key: str = lemma_key
        self.disambiguation_key: str = disambiguation_key
        self.match_pattern: re.Regex = re.compile(match_pattern)

    def disambiguate(self, file_path: str, config: "CorpusConfiguration"):
        temp = tempfile.TemporaryFile(mode="w+")  # 2

        try:
            with open(file_path) as file:
                csv_reader = csv.reader(file, delimiter=config.column_marker)
                header: List[str] = []
                for nb_line, line in enumerate(csv_reader):  # The file should already have been open
                    if nb_line == 0:
                        temp.write(config.column_marker.join(line+[self.disambiguation_key])+"\n")
                        header = line
                        continue
                    elif not line:
                        temp.write("\n")
                        continue
                    lines = dict(zip(header, line))

                    found = self.match_pattern.findall(lines[self.lemma_key])
                    if found:
                        lines[self.disambiguation_key] = found[0]
                        lines[self.lemma_key] = self.match_pattern.sub("", lines[self.lemma_key])
                        print(lines)
                    temp.write(config.column_marker.join(list(lines.values()))+"\n")
            with open(file_path, "w") as f:
                temp.seek(0)
                f.write(temp.read())
        finally:
            temp.close()  # 5

    @staticmethod
    def from_xml(disambiguation_node: Element) -> "Disambiguation":
        return Disambiguation(
            lemma_key=disambiguation_node.attrib["lemma-column-name"],
            disambiguation_key=disambiguation_node.attrib["disambiguation-column-name"],
            match_pattern=disambiguation_node.attrib["matchPattern"]
        )
