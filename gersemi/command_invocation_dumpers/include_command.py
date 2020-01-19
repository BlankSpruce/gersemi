from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class IncludeCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 1
    options = ["OPTIONAL", "NO_POLICY_SCOPE"]
    one_value_keywords = ["RESULT_VARIABLE"]
