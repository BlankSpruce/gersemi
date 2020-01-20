from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class MessageCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "FATAL_ERROR",
        "SEND_ERROR",
        "WARNING",
        "AUTHOR_WARNING",
        "DEPRECATION",
        "NOTICE",
        "STATUS",
        "VERBOSE",
        "DEBUG",
        "TRACE",
    ]
