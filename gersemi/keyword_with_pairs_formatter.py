from gersemi.ast_helpers import is_comment
from gersemi.base_dumper import BaseDumper


class KeywordWithPairsFormatter(BaseDumper):
    def _format_pair(self, key, value):
        result = self._try_to_format_into_single_line([key, value], separator=" ")
        if result is not None:
            return result

        formatted_key = self.visit(key)
        with self.indented():
            formatted_value = self.visit(value)
        return "\n".join([formatted_key, formatted_value])

    def _format_keyword_with_pairs(self, args):
        lines = []
        iterator = iter(args)
        for arg in iterator:
            if is_comment(arg):
                lines.append(self.visit(arg))
                continue

            key = arg
            value = next(iterator, None)
            if value is None:
                line = self.visit(key)
            else:
                line = self._format_pair(key, value)
            lines.append(line)
        return "\n".join(lines)
