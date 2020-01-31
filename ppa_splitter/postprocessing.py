from .reader import Reader
import tempfile
import regex as re
from xml.etree.ElementTree import Element


class Disambiguation(object):
    def __init__(self, lemma_key: str, disambiguation_key: str, match_pattern: str):
        self.lemma_key: str = lemma_key
        self.disambiguation_key: str = disambiguation_key
        self.match_pattern: re.Regex = re.compile(match_pattern)

    def disambiguate(self, file_path: str, reader: Reader):
        temp = tempfile.TemporaryFile()  # 2

        try:
            with open(file_path) as file:
                for nb_line, line in enumerate(file.read()):  # The file should already have been open
                    if nb_line == 0:
                        temp.write(line)
                        continue
                    lemma_column = reader.read(line)
                    found = self.match_pattern.findall(lemma_column)
                    if found:
                        print(found)
                    temp.write(line)

        finally:
            temp.close()  # 5

    @staticmethod
    def from_xml(disambiguation_node: Element) -> "Disambiguation":
        return Disambiguation(
            lemma_key=disambiguation_node.attrib["lemma-column-name"],
            disambiguation_key=disambiguation_node.attrib["disambiguation-column-name"],
            match_pattern=disambiguation_node.attrib["matchPattern"]
        )
