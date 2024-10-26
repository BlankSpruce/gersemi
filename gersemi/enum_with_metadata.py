from enum import Enum
import textwrap


def doc(text: str) -> str:
    return " ".join(textwrap.dedent(text).splitlines()).strip()


class EnumWithMetadata(Enum):
    def __new__(cls, data):
        self = object.__new__(cls)
        self._value_ = data["value"]
        self.description = doc(data["description"])
        self.title = data["title"]
        return self

    def __repr__(self):
        return self.value
