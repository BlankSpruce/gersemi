from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class CMakeHostSysteInformationCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RESULT"]
    multi_value_keywords = ["QUERY"]


class ConfigureFileCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 2
    options = ["COPYONLY", "ESCAPE_QUOTES", "@ONLY"]
    one_value_keywords = ["NEWLINE_STYLE"]


class EndMacroCommandDumper(ArgumentAwareCommandInvocationDumper):
    pass


class ExecuteProcessCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "OUTPUT_QUIET",
        "ERROR_QUIET",
        "OUTPUT_STRIP_TRAILING_WHITESPACE",
        "ERROR_STRIP_TRAILING_WHITESPACE",
    ]
    one_value_keywords = [
        "WORKING_DIRECTORY",
        "TIMEOUT",
        "RESULT_VARIABLE",
        "RESULTS_VARIABLE",
        "OUTPUT_VARIABLE",
        "ERROR_VARIABLE",
        "INPUT_FILE",
        "OUTPUT_FILE",
        "ERROR_FILE",
        "COMMAND_ECHO",
        "ENCODING",
    ]
    multi_value_keywords = ["COMMAND"]


class GetDirectoryPropertyCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 1
    one_value_keywords = ["DIRECTORY", "DEFINITION"]
    back_optional_args = 1


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


class IncludeCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 1
    options = ["OPTIONAL", "NO_POLICY_SCOPE"]
    one_value_keywords = ["RESULT_VARIABLE"]


class MacroCommandDumper(ArgumentAwareCommandInvocationDumper):
    pass


class MarkAsAdvancedCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["CLEAR", "FORCE"]


class MathCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["OUTPUT_FORMAT"]
    multi_value_keywords = ["EXPR"]


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


class SeparateArgumentsCommandDumper(ArgumentAwareCommandInvocationDumper):
    pass


class SetPropertyCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["GLOBAL", "APPEND", "APPEND_STRING"]
    one_value_keywords = ["DIRECTORY"]
    multi_value_keywords = ["TARGET", "SOURCE", "INSTALL", "TEST", "CACHE", "PROPERTY"]
