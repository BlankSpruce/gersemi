from gersemi.ast_helpers import is_comment, pair
from gersemi.base_dumper import BaseDumper
from gersemi.utils import pop_all


class KeywordWithPairsFormatter(BaseDumper):
    def _pair_arguments(self, args):
        result = []
        accumulator = []
        for arg in args:
            if accumulator:
                accumulator.append(arg)
                if not is_comment(arg):
                    result.append(pair(pop_all(accumulator)))
            else:
                if is_comment(arg):
                    result.append(arg)
                else:
                    accumulator.append(arg)

        if accumulator:
            result.append(pair(pop_all(accumulator)))

        return result

    def _format_keyword_with_pairs(self, args):
        return "\n".join(map(self.visit, self._pair_arguments(args)))
