from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class GetFilenameComponentCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 2
    options = [
        "DIRECTORY",
        "NAME",
        "EXT",
        "NAME_WE",
        "LAST_EXT",
        "NAME_WLE",
        "PATH",
        "PROGRAM",
        "CACHE",
    ]
    one_value_keywords = ["BASE_DIR", "PROGRAM_ARGS"]
