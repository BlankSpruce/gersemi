from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class GetPropertyCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 1
    options = ["GLOBAL", "VARIABLE", "SET", "DEFINED", "BRIEF_DOCS", "FULL_DOCS"]
    one_value_keywords = [
        "TARGET",
        "SOURCE",
        "INSTALL",
        "TEST",
        "CACHE",
        "PROPERTY",
    ]
    multi_value_keywords = ["DIRECTORY"]
