class WidthLimitingBuffer:
    def __init__(self, width: int):
        self.width = width
        self.lines = [""]

    def __iadd__(self, text: str):
        if text == "\n":
            self.lines.append("")
        elif text == " " and len(self.lines[-1]) == self.width:
            return self
        elif "\n" in text:
            for item in text.split("\n"):
                self += item
                self += "\n"
        elif len(self.lines[-1]) + len(text) > self.width and self.lines[-1] != "":
            self.lines.append(text)
        else:
            self.lines[-1] += text
        return self

    def _remove_ending_newlines(self) -> None:
        while len(self.lines) > 0 and self.lines[-1] == "":
            self.lines.pop()

    def __str__(self) -> str:
        self._remove_ending_newlines()
        return "\n".join(map(str.rstrip, self.lines))
