from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .command_with_property_value_pairs_dumper import (
    CommandWithPropertyValuePairsDumper,
)
from .condition_syntax_command_invocation_dumper import (
    ConditionSyntaxCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .set_command import SetCommandDumper


class CMakeHostSysteInformationCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RESULT"]
    multi_value_keywords = ["QUERY"]


class CMakeParseArgumentsCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["PARSE_ARGV"]


class ConfigureFileCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["COPYONLY", "ESCAPE_QUOTES", "@ONLY"]
    one_value_keywords = ["NEWLINE_STYLE"]


class EndForeachCommandDumper(ArgumentAwareCommandInvocationDumper):
    pass


class EndFunctionCommandDumper(ArgumentAwareCommandInvocationDumper):
    pass


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


class FileCommandDumper(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        # Reading
        "READ": dict(
            options=["HEX"],
            one_value_keywords=["OFFSET", "LIMIT"],
            multi_value_keywords=["READ"],
        ),
        "STRINGS": dict(
            options=["NEWLINE_CONSUME", "NO_HEX_CONVERSION"],
            one_value_keywords=[
                "LENGTH_MAXIMUM",
                "LENGTH_MINIMUM",
                "LIMIT_COUNT",
                "LIMIT_INPUT",
                "LIMIT_OUTPUT",
                "REGEX",
                "ENCODING",
            ],
            multi_value_keywords=["STRINGS"],
        ),
        "GET_RUNTIME_DEPENDENCIES": dict(
            one_value_keywords=[
                "RESOLVED_DEPENDENCIES_VAR",
                "UNRESOLVED_DEPENDENCIES_VAR",
                "CONFLICTING_DEPENDENCIES_PREFIX",
                "BUNDLE_EXECUTABLE",
            ],
            multi_value_keywords=[
                "EXECUTABLES",
                "LIBRARIES",
                "MODULES",
                "DIRECTORIES",
                "PRE_INCLUDE_REGEXES",
                "PRE_EXCLUDE_REGEXES",
                "POST_INCLUDE_REGEXES",
                "POST_EXCLUDE_REGEXES",
            ],
        ),
        # Writing
        "GENERATE": dict(
            one_value_keywords=["INPUT", "CONTENT", "CONDITION"],
            multi_value_keywords=["GENERATE"],
        ),
        # Filesystem
        "GLOB": dict(
            options=["CONFIGURE_DEPENDS"],
            one_value_keywords=["GLOB", "LIST_DIRECTORIES", "RELATIVE"],
        ),
        "GLOB_RECURSE": dict(
            options=["CONFIGURE_DEPENDS"],
            one_value_keywords=["GLOB_RECURSE", "LIST_DIRECTORIES", "RELATIVE"],
        ),
        "COPY": dict(
            options=[
                "NO_SOURCE_PERMISSIONS",
                "USE_SOURCE_PERMISSIONS",
                "FOLLOW_SYMLINK_CHAIN",
                "FILES_MATCHING",
                "EXCLUDE",
            ],
            one_value_keywords=["DESTINATION", "PATTERN", "REGEX"],
            multi_value_keywords=[
                "COPY",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
                "PERMISSIONS",
            ],
        ),
        "INSTALL": dict(
            options=[
                "NO_SOURCE_PERMISSIONS",
                "USE_SOURCE_PERMISSIONS",
                "FOLLOW_SYMLINK_CHAIN",
                "FILES_MATCHING",
                "EXCLUDE",
            ],
            one_value_keywords=["DESTINATION", "PATTERN", "REGEX"],
            multi_value_keywords=[
                "INSTALL",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
                "PERMISSIONS",
            ],
        ),
        "CREATE_LINK": dict(
            options=["COPY_ON_ERROR", "SYMBOLIC"],
            one_value_keywords=["RESULT"],
            multi_value_keywords=["CREATE_LINK"],
        ),
        # Transfer
        "DOWNLOAD": dict(
            options=["SHOW_PROGRESS"],
            one_value_keywords=[
                "INACTIVITY_TIMEOUT",
                "LOG",
                "STATUS",
                "TIMEOUT",
                "USERPWD",
                "HTTPHEADER",
                "NETRC",
                "NETRC_FILE",
                "EXPECTED_HASH",
                "EXPECTED_MD5",
                "TLS_VERIFY",
                "TLS_CAINFO",
            ],
            multi_value_keywords=["DOWNLOAD"],
        ),
        "UPLOAD": dict(
            options=["SHOW_PROGRESS"],
            one_value_keywords=[
                "INACTIVITY_TIMEOUT",
                "LOG",
                "STATUS",
                "TIMEOUT",
                "USERPWD",
                "HTTPHEADER",
                "NETRC",
                "NETRC_FILE",
            ],
            multi_value_keywords=["UPLOAD"],
        ),
        # Locking
        "LOCK": dict(
            options=["DIRECTORY", "RELEASE"],
            one_value_keywords=["LOCK", "GUARD", "RESULT_VARIABLE", "TIMEOUT"],
        ),
    }


class FindFileCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "NO_DEFAULT_PATH",
        "NO_PACKAGE_ROOT_PATH",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "NO_SYSTEM_ENVIRONMENT_PATH",
        "NO_CMAKE_SYSTEM_PATH",
        "CMAKE_FIND_ROOT_PATH_BOTH",
        "ONLY_CMAKE_FIND_ROOT_PATH",
        "NO_CMAKE_FIND_ROOT_PATH",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class FindLibraryCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "NAMES_PER_DIR",
        "NO_DEFAULT_PATH",
        "NO_PACKAGE_ROOT_PATH",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "NO_SYSTEM_ENVIRONMENT_PATH",
        "NO_CMAKE_SYSTEM_PATH",
        "CMAKE_FIND_ROOT_PATH_BOTH",
        "ONLY_CMAKE_FIND_ROOT_PATH",
        "NO_CMAKE_FIND_ROOT_PATH",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class FindPackageCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "EXACT",
        "QUIET",
        "MODULE",
        "CONFIG",
        "NO_MODULE",
        "NO_POLICY_SCOPE",
        "NO_DEFAULT_PATH",
        "NO_PACKAGE_ROOT_PATH",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "NO_SYSTEM_ENVIRONMENT_PATH",
        "NO_CMAKE_PACKAGE_REGISTRY",
        "NO_CMAKE_BUILDS_PATH",
        "NO_CMAKE_SYSTEM_PATH",
        "NO_CMAKE_SYSTEM_PACKAGE_REGISTRY",
        "CMAKE_FIND_ROOT_PATH_BOTH",
        "ONLY_CMAKE_FIND_ROOT_PATH",
        "NO_CMAKE_FIND_ROOT_PATH",
    ]
    multi_value_keywords = [
        "REQUIRED",
        "COMPONENTS",
        "OPTIONAL_COMPONENTS",
        "NAMES",
        "CONFIGS",
        "HINTS",
        "PATHS",
        "PATH_SUFFIXES",
    ]


class FindPathCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "NO_DEFAULT_PATH",
        "NO_PACKAGE_ROOT_PATH",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "NO_SYSTEM_ENVIRONMENT_PATH",
        "NO_CMAKE_SYSTEM_PATH",
        "CMAKE_FIND_ROOT_PATH_BOTH",
        "ONLY_CMAKE_FIND_ROOT_PATH",
        "NO_CMAKE_FIND_ROOT_PATH",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class FindProgramCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = [
        "NAMES_PER_DIR",
        "NO_DEFAULT_PATH",
        "NO_PACKAGE_ROOT_PATH",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "NO_SYSTEM_ENVIRONMENT_PATH",
        "NO_CMAKE_SYSTEM_PATH",
        "CMAKE_FIND_ROOT_PATH_BOTH",
        "ONLY_CMAKE_FIND_ROOT_PATH",
        "NO_CMAKE_FIND_ROOT_PATH",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class ForeachCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["IN"]
    multi_value_keywords = ["RANGE", "LISTS", "ITEMS"]


class FunctionCommandDumper(ArgumentAwareCommandInvocationDumper):
    pass


class GetDirectoryPropertyCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DIRECTORY", "DEFINITION"]


class GetFilenameComponentCommandDumper(ArgumentAwareCommandInvocationDumper):
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
    options = ["OPTIONAL", "NO_POLICY_SCOPE"]
    one_value_keywords = ["RESULT_VARIABLE"]


class ListCommandDumper(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        # Modification
        "FILTER": dict(
            options=["INCLUDE", "EXCLUDE"], one_value_keywords=["FILTER", "REGEX"],
        ),
        "REMOVE_DUPLICATES": dict(one_value_keywords=["REMOVE_DUPLICATES"],),
        "TRANSFORM": dict(
            one_value_keywords=["OUTPUT_VARIABLE"],
            multi_value_keywords=[
                "TRANSFORM",
                "APPEND",
                "PREPEND",
                "TOLOWER",
                "TOUPPER",
                "STRIP",
                "GENEX_STRIP",
                "REPLACE",
            ],
        ),
        # Ordering
        "SORT": dict(one_value_keywords=["SORT", "COMPARE", "CASE", "ORDER"],),
    }


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


class StringCommandDumper(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        # Search and Replace
        "FIND": dict(options=["REVERSE"], multi_value_keywords=["FIND"],),
        # Regular Expressions
        "REGEX": dict(one_value_keywords=["REGEX"],),
        # Comparison
        "COMPARE": dict(one_value_keywords=["COMPARE"],),
        # Generation
        "CONFIGURE": dict(
            options=["@ONLY", "ESCAPE_QUOTES"], multi_value_keywords=["CONFIGURE"],
        ),
        "RANDOM": dict(one_value_keywords=["LENGTH", "ALPHABET", "RANDOM_SEED"],),
        "UUID": dict(
            options=["UPPER"], one_value_keywords=["UUID", "NAMESPACE", "NAME", "TYPE"],
        ),
    }


scripting_command_mapping = {
    "cmake_host_system_information": CMakeHostSysteInformationCommandDumper,
    "cmake_parse_arguments": CMakeParseArgumentsCommandDumper,
    "configure_file": ConfigureFileCommandDumper,
    "elseif": ConditionSyntaxCommandInvocationDumper,
    "else": ConditionSyntaxCommandInvocationDumper,
    "endif": ConditionSyntaxCommandInvocationDumper,
    "endforeach": EndForeachCommandDumper,
    "endfunction": EndFunctionCommandDumper,
    "endmacro": EndMacroCommandDumper,
    "endwhile": ConditionSyntaxCommandInvocationDumper,
    "execute_process": ExecuteProcessCommandDumper,
    "file": FileCommandDumper,
    "find_file": FindFileCommandDumper,
    "find_library": FindLibraryCommandDumper,
    "find_package": FindPackageCommandDumper,
    "find_path": FindPathCommandDumper,
    "find_program": FindProgramCommandDumper,
    "foreach": ForeachCommandDumper,
    "function": FunctionCommandDumper,
    "get_directory_property": GetDirectoryPropertyCommandDumper,
    "get_filename_component": GetFilenameComponentCommandDumper,
    "get_property": GetPropertyCommandDumper,
    "if": ConditionSyntaxCommandInvocationDumper,
    "include": IncludeCommandDumper,
    "list": ListCommandDumper,
    "macro": MacroCommandDumper,
    "mark_as_advanced": MarkAsAdvancedCommandDumper,
    "math": MathCommandDumper,
    "message": MessageCommandDumper,
    "separate_arguments": SeparateArgumentsCommandDumper,
    "set_directory_properties": CommandWithPropertyValuePairsDumper,
    "set_property": SetPropertyCommandDumper,
    "set": SetCommandDumper,
    "string": StringCommandDumper,
    "while": ConditionSyntaxCommandInvocationDumper,
}
