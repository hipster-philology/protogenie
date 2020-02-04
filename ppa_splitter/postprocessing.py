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


class ApplyTo:
    def __init__(self, source: str, target: List[str]):
        self.source: str = source
        self.target: List[str] = target

    @staticmethod
    def from_xml(apply_to_node: Element) -> "ApplyTo":
        return ApplyTo(
            source=apply_to_node.attrib["source"],
            target=[str(node.text).strip() for node in apply_to_node.findall("./target")]
        )


class ReplacementSet(object):
    def __init__(
            self, match_pattern: str, replacement_pattern: str,
            applies_to: List[ApplyTo]
    ):
        self.match_pattern: re.Regex = re.compile(match_pattern)
        self.replacement_pattern: str = replacement_pattern
        self.applies_to: List[ApplyTo] = applies_to

    def replace(self, file_path: str, config: "CorpusConfiguration"):
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

    @staticmethod
    def from_xml(replacement_node: Element) -> "ReplacementSet":
        return ReplacementSet(
            match_pattern=replacement_node.attrib["matchPattern"],
            replacement_pattern=replacement_node.attrib["replacementPattern"],
            applies_to=[ApplyTo.from_xml(node) for node in replacement_node.findall("applyTo")]
        )


class Skip(object):
    def __init__(
        self, match_pattern: str, target: str
    ):
        self.match_pattern: re.Regex = re.compile(match_pattern)
        self.target: str = target

    def replace(self, file_path: str, config: "CorpusConfiguration"):
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

                    # If it matches, we skip it
                    if self.match_pattern.search(lines[self.target]):
                        continue

                    temp.write(config.column_marker.join(list(lines.values()))+"\n")

            with open(file_path, "w") as f:
                temp.seek(0)
                f.write(temp.read())
        finally:
            temp.close()  # 5

    @staticmethod
    def from_xml(skip_node: Element) -> "Skip":
        return Skip(
            match_pattern=skip_node.attrib["matchPattern"],
            target=skip_node.attrib["target"]
        )
