from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class MathCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["OUTPUT_FORMAT"]
    multi_value_keywords = ["EXPR"]
