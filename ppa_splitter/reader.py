from typing import List, Tuple, Dict, Union, Optional
from xml.etree import ElementTree


class Reader(object):
    def __init__(self, reader_type: str, keys: List[Tuple[str, str]]):
        self.map_to: Dict[Union[int, str], str] = {}
        self.reader_type: str = reader_type

        if self.reader_type == "order":
            self.map_to = {int(key): mapped for key, mapped in keys}
        elif self.reader_type == "explicit":
            self.map_to = {key: mapped or key for key, mapped in keys}

    @property
    def has_header(self):
        return self.reader_type == "explicit"

    @classmethod
    def from_xml(cls, xml_node: ElementTree, default: Optional["Reader"] = None) -> "Reader":
        reader_type = xml_node.get("type")
        if reader_type == "default":
            return default
        _map = [(key.text.strip(), key.get("map-to")) for key in xml_node.findall("./key")]
        return cls(reader_type=reader_type, keys=_map)

    @property
    def header(self):
        return [
            self.map_to.get(item, None)
            for item in range(max(self.map_to.keys())+1)
        ]

    def map(self, line: Union[List[str], Dict[str, str]]) -> Dict[str, str]:
        return None

    def __repr__(self):
        return "<Reader type='{}' keys=[{}] from=[{}] />".format(
            self.reader_type,
            ", ".join(self.map_to.values()),
            ", ".join(list(map(str, self.map_to.keys())))
        )