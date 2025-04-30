from gersemi.ast_helpers import is_comment
from gersemi.base_dumper import BaseDumper
from gersemi.utils import pop_all


class SortingPreprocessor(BaseDumper):
    def _get_bucket_value(self, bucket):
        *comments, node = bucket
        return self.visit(node), [self.visit(comment) for comment in comments]

    def _bucket_arguments_with_their_preceding_comments(self, args):
        result = []
        accumulator = []
        for arg in args:
            accumulator.append(arg)
            if not is_comment(arg):
                result.append(pop_all(accumulator))

        if accumulator:
            result.append(pop_all(accumulator))

        return result

    def _sort_arguments(self, args):
        buckets = self._bucket_arguments_with_their_preceding_comments(args)
        sorted_buckets = sorted(buckets, key=self._get_bucket_value)

        return [arg for bucket in sorted_buckets for arg in bucket]
