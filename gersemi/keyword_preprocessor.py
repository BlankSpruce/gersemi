from gersemi.ast_helpers import is_comment
from gersemi.base_dumper import BaseDumper
from gersemi.utils import pop_all


class KeywordPreprocessor(BaseDumper):
    def _get_bucket_value(self, bucket):
        *comments, node = bucket
        return self.visit(node), tuple(self.visit(comment) for comment in comments)

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

    def _keep_unique_arguments(self, args):
        buckets = self._bucket_arguments_with_their_preceding_comments(args)
        known = set()
        unique_buckets = []
        for bucket in buckets:
            value = self._get_bucket_value(bucket)
            if value not in known:
                known.add(value)
                unique_buckets.append(bucket)

        return [arg for bucket in unique_buckets for arg in bucket]

    def _sort_and_keep_unique_arguments(self, args):
        return self._sort_arguments(self._keep_unique_arguments(args))
