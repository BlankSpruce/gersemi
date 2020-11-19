from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .condition_syntax_command_invocation_dumper import (
    ConditionSyntaxCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .set_command import Set


class CMakeHostSysteInformation(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RESULT"]
    multi_value_keywords = ["QUERY"]


class CMakeLanguage(ArgumentAwareCommandInvocationDumper):
    options = ["DEFER", "EVAL"]
    one_value_keywords = ["DIRECTORY", "ID", "ID_VAR", "GET_CALL_IDS", "GET_CALL"]
    multi_value_keywords = ["CALL", "CANCEL_CALL"]


class CMakeParseArguments(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["PARSE_ARGV"]


class ConfigureFile(ArgumentAwareCommandInvocationDumper):
    options = ["COPYONLY", "ESCAPE_QUOTES", "@ONLY", "NO_SOURCE_PERMISSIONS"]
    one_value_keywords = ["NEWLINE_STYLE"]


class EndForeach(ArgumentAwareCommandInvocationDumper):
    pass


class EndFunction(ArgumentAwareCommandInvocationDumper):
    pass


class EndMacro(ArgumentAwareCommandInvocationDumper):
    pass


class ExecuteProcess(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    options = [
        "OUTPUT_QUIET",
        "ERROR_QUIET",
        "OUTPUT_STRIP_TRAILING_WHITESPACE",
        "ERROR_STRIP_TRAILING_WHITESPACE",
        "ECHO_OUTPUT_VARIABLE",
        "ECHO_ERROR_VARIABLE",
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
        "COMMAND_ERROR_IS_FATAL",
    ]
    multi_value_keywords = ["COMMAND"]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class File(MultipleSignatureCommandInvocationDumper):
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
            one_value_keywords=["INPUT", "CONTENT", "CONDITION", "OUTPUT", "TARGET"],
        ),
        "CONFIGURE": dict(
            options=["ESCAPE_QUOTES", "@ONLY"],
            one_value_keywords=["OUTPUT", "CONTENT", "NEWLINE_STYLE"],
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
        "CHMOD": dict(
            multi_value_keywords=[
                "PERMISSIONS",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
            ]
        ),
        "CHMOD_RECURSE": dict(
            multi_value_keywords=[
                "PERMISSIONS",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
            ]
        ),
        # Path Conversion
        "REAL_PATH": dict(one_value_keywords=["BASE_DIRECTORY"]),
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
                "TLS_VERIFY",
                "TLS_CAINFO",
            ],
            multi_value_keywords=["UPLOAD"],
        ),
        # Locking
        "LOCK": dict(
            options=["DIRECTORY", "RELEASE"],
            one_value_keywords=["LOCK", "GUARD", "RESULT_VARIABLE", "TIMEOUT"],
        ),
        # Archiving
        "ARCHIVE_CREATE": dict(
            options=["VERBOSE"],
            one_value_keywords=[
                "OUTPUT",
                "FORMAT",
                "COMPRESSION",
                "COMPRESSION_LEVEL",
                "MTIME",
            ],
            multi_value_keywords=["PATHS"],
        ),
        "ARCHIVE_EXTRACT": dict(
            options=["LIST_ONLY", "VERBOSE"],
            one_value_keywords=["INPUT", "DESTINATION"],
            multi_value_keywords=["PATTERNS"],
        ),
    }


class FindFile(ArgumentAwareCommandInvocationDumper):
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
        "REQUIRED",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class FindLibrary(ArgumentAwareCommandInvocationDumper):
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
        "REQUIRED",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class FindPackage(ArgumentAwareCommandInvocationDumper):
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


class FindPath(ArgumentAwareCommandInvocationDumper):
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
        "REQUIRED",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class FindProgram(ArgumentAwareCommandInvocationDumper):
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
        "REQUIRED",
    ]
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"]


class Foreach(ArgumentAwareCommandInvocationDumper):
    options = ["IN"]
    multi_value_keywords = ["RANGE", "LISTS", "ITEMS", "ZIP_LISTS"]


class Function(ArgumentAwareCommandInvocationDumper):
    pass


class GetDirectoryProperty(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DIRECTORY", "DEFINITION"]


class GetFilenameComponent(ArgumentAwareCommandInvocationDumper):
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


class GetProperty(ArgumentAwareCommandInvocationDumper):
    options = ["GLOBAL", "VARIABLE", "SET", "DEFINED", "BRIEF_DOCS", "FULL_DOCS"]
    one_value_keywords = ["TARGET", "INSTALL", "TEST", "CACHE", "PROPERTY"]
    multi_value_keywords = ["DIRECTORY", "SOURCE"]


class GetSourceFileProperty(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DIRECTORY", "TARGET_DIRECTORY"]


class Include(ArgumentAwareCommandInvocationDumper):
    options = ["OPTIONAL", "NO_POLICY_SCOPE"]
    one_value_keywords = ["RESULT_VARIABLE"]


class List(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        # Modification
        "FILTER": dict(
            options=["INCLUDE", "EXCLUDE"], one_value_keywords=["FILTER", "REGEX"]
        ),
        "REMOVE_DUPLICATES": dict(one_value_keywords=["REMOVE_DUPLICATES"]),
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
        "SORT": dict(one_value_keywords=["SORT", "COMPARE", "CASE", "ORDER"]),
    }


class Macro(ArgumentAwareCommandInvocationDumper):
    pass


class MarkAsAdvanced(ArgumentAwareCommandInvocationDumper):
    options = ["CLEAR", "FORCE"]


class Math(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["OUTPUT_FORMAT"]
    multi_value_keywords = ["EXPR"]


class Message(ArgumentAwareCommandInvocationDumper):
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
        "CHECK_START",
        "CHECK_PASS",
        "CHECK_FAIL",
    ]


class SeparateArguments(ArgumentAwareCommandInvocationDumper):
    options = ["PROGRAM", "SEPARATE_ARGS"]


class SetProperty(ArgumentAwareCommandInvocationDumper):
    options = ["GLOBAL", "APPEND", "APPEND_STRING"]
    one_value_keywords = ["DIRECTORY"]
    multi_value_keywords = ["TARGET", "SOURCE", "INSTALL", "TEST", "CACHE", "PROPERTY"]


class String(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        # Search and Replace
        "FIND": dict(options=["REVERSE"], multi_value_keywords=["FIND"]),
        # Regular Expressions
        "REGEX": dict(one_value_keywords=["REGEX"]),
        # Comparison
        "COMPARE": dict(one_value_keywords=["COMPARE"]),
        # Generation
        "CONFIGURE": dict(
            options=["@ONLY", "ESCAPE_QUOTES"], multi_value_keywords=["CONFIGURE"]
        ),
        "RANDOM": dict(one_value_keywords=["LENGTH", "ALPHABET", "RANDOM_SEED"]),
        "UUID": dict(
            options=["UPPER"], one_value_keywords=["UUID", "NAMESPACE", "NAME", "TYPE"]
        ),
        # JSON
        "JSON": dict(
            one_value_keywords=[
                "ERROR_VARIABLE",
                "GET",
                "TYPE",
                "MEMBER",
                "LENGTH",
                "REMOVE",
                "SET",
            ],
            multi_value_keywords=["EQUAL"],
        ),
    }


class SetDirectoryProperties(
    KeywordWithPairsFormatter, ArgumentAwareCommandInvocationDumper
):
    multi_value_keywords = ["PROPERTIES"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


scripting_command_mapping = {
    "cmake_host_system_information": CMakeHostSysteInformation,
    "cmake_language": CMakeLanguage,
    "cmake_parse_arguments": CMakeParseArguments,
    "configure_file": ConfigureFile,
    "elseif": ConditionSyntaxCommandInvocationDumper,
    "else": ConditionSyntaxCommandInvocationDumper,
    "endif": ConditionSyntaxCommandInvocationDumper,
    "endforeach": EndForeach,
    "endfunction": EndFunction,
    "endmacro": EndMacro,
    "endwhile": ConditionSyntaxCommandInvocationDumper,
    "execute_process": ExecuteProcess,
    "file": File,
    "find_file": FindFile,
    "find_library": FindLibrary,
    "find_package": FindPackage,
    "find_path": FindPath,
    "find_program": FindProgram,
    "foreach": Foreach,
    "function": Function,
    "get_directory_property": GetDirectoryProperty,
    "get_filename_component": GetFilenameComponent,
    "get_property": GetProperty,
    "get_source_file_property": GetSourceFileProperty,
    "if": ConditionSyntaxCommandInvocationDumper,
    "include": Include,
    "list": List,
    "macro": Macro,
    "mark_as_advanced": MarkAsAdvanced,
    "math": Math,
    "message": Message,
    "separate_arguments": SeparateArguments,
    "set_directory_properties": SetDirectoryProperties,
    "set_property": SetProperty,
    "set": Set,
    "string": String,
    "while": ConditionSyntaxCommandInvocationDumper,
}
