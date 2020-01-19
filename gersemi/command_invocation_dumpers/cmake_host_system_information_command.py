from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class CMakeHostSysteInformationCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RESULT"]
    multi_value_keywords = ["QUERY"]
