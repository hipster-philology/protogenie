if False:
    from .configs import CorpusConfiguration
import tempfile
import regex as re
from xml.etree.ElementTree import Element
import csv
from typing import List, ClassVar
from abc import ABC, abstractmethod


class PostProcessing(ABC):
    NodeName = "XML-NODE-LOCAL-NAME"  # Name of the node to match

    @abstractmethod
    def apply(self, file_path: str, config: "CorpusConfiguration"):
        raise NotImplementedError

    @abstractmethod
    def from_xml(cls, node: Element) -> ClassVar["PostProcessing"]:
        raise NotImplementedError

    @classmethod
    def match_config_node(cls, node: Element) -> bool:
        """ If the current node is representing the current object, returns True
        """
        return node.tag == cls.NodeName


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


class Disambiguation(PostProcessing):
    NodeName = "disambiguation"

    def __init__(self, lemma_key: str, disambiguation_key: str, match_pattern: str,
                 default_value: str, keep: bool = False):
        super(Disambiguation, self).__init__()
        self.lemma_key: str = lemma_key
        self.disambiguation_key: str = disambiguation_key
        self.match_pattern: re.Regex = re.compile(match_pattern)
        self.keep: bool = keep
        self.default_value: str = default_value

    def apply(self, file_path: str, config: "CorpusConfiguration"):
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
                        if not self.keep:  # If we do not keep the original value, we remove it
                            lines[self.lemma_key] = self.match_pattern.sub("", lines[self.lemma_key])
                    else:
                        lines[self.disambiguation_key] = self.default_value

                    temp.write(config.column_marker.join(list(lines.values()))+"\n")
            with open(file_path, "w") as f:
                temp.seek(0)
                f.write(temp.read())
        finally:
            temp.close()  # 5

    @classmethod
    def from_xml(cls, node: Element) -> "Disambiguation":
        return cls(
            lemma_key=node.attrib["source-column"],
            disambiguation_key=node.attrib["new-column"],
            match_pattern=node.attrib["matchPattern"],
            keep="keep" in node.attrib,
            default_value=node.attrib.get("default", "_")
        )


class ReplacementSet(PostProcessing):
    """ Using a regular expression, replaces values in certain columns
    """
    NodeName = "replacement"

    def __init__(
            self, match_pattern: str, replacement_pattern: str,
            applies_to: List[ApplyTo]
    ):
        super(ReplacementSet, self).__init__()
        self.match_pattern: re.Regex = re.compile(match_pattern)
        self.replacement_pattern: str = replacement_pattern
        self.applies_to: List[ApplyTo] = applies_to

    def apply(self, file_path: str, config: "CorpusConfiguration"):
        temp = tempfile.TemporaryFile(mode="w+")
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
    def from_xml(cls, node: Element) -> "ReplacementSet":
        return ReplacementSet(
            match_pattern=node.attrib["matchPattern"],
            replacement_pattern=node.attrib["replacementPattern"],
            applies_to=[ApplyTo.from_xml(apply_to) for apply_to in node.findall("applyTo")]
        )


class Skip(PostProcessing):
    """ If the matchPattern matches target column, the line is removed from the post-processed output
    """
    NodeName = "skip"

    def __init__(
        self, match_pattern: str, source: str
    ):
        super(Skip, self).__init__()
        self.match_pattern: re.Regex = re.compile(match_pattern)
        self.source: str = source

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

                    # If it matches, we skip it
                    if self.match_pattern.search(lines[self.source]):
                        continue

                    temp.write(config.column_marker.join(list(lines.values()))+"\n")

            with open(file_path, "w") as f:
                temp.seek(0)
                f.write(temp.read())
        finally:
            temp.close()  # 5

    @classmethod
    def from_xml(cls, node: Element) -> "Skip":
        return Skip(
            match_pattern=node.attrib["matchPattern"],
            source=node.attrib["source"]
        )
