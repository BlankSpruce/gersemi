from gersemi.argument_schema import ArgumentSchema
from gersemi.dumper import Dumper


class SetProperty(Dumper):
    schema = ArgumentSchema(
        options=["GLOBAL", "APPEND", "APPEND_STRING"],
        multi_value_keywords=[
            "TARGET",
            "SOURCE",
            "INSTALL",
            "TEST",
            "CACHE",
            "PROPERTY",
            "TARGET_DIRECTORIES",
            "DIRECTORY",
            "FILE_SET",
        ],
    )
    _keyword_formatters = {"PROPERTY": "_format_property"}

    def _format_property(self, args):
        result = self._try_to_format_into_single_line(
            args, prefix="", postfix="", visitor=self.arguments_atom
        )
        if result is not None:
            return result

        name, *rest = args
        with self.indented():
            formatted_rest = "\n".join(map(self.arguments_atom, rest))
        return f"{self.arguments_atom(name)}\n{formatted_rest}"


set_property = {"set_property": {"__impl": SetProperty}}
