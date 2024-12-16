# pylint: disable=too-many-lines
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .condition_syntax_command_invocation_dumper import (
    ConditionSyntaxCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .two_word_keyword_isolator import TwoWordKeywordIsolator


_COMPARE_EQUAL = ("COMPARE", "EQUAL")
_COMPARE_GREATER = ("COMPARE", "GREATER")
_COMPARE_GREATER_EQUAL = ("COMPARE", "GREATER_EQUAL")
_COMPARE_LESS = ("COMPARE", "LESS")
_COMPARE_LESS_EQUAL = ("COMPARE", "LESS_EQUAL")
_COMPARE_NOTEQUAL = ("COMPARE", "NOTEQUAL")
_EVAL_CODE = ("EVAL", "CODE")
_EXTENSION_LAST_ONLY = ("EXTENSION", "LAST_ONLY")
_QUERY_WINDOWS_REGISTRY = ("QUERY", "WINDOWS_REGISTRY")
_REGEX_MATCH = ("REGEX", "MATCH")
_REGEX_MATCHALL = ("REGEX", "MATCHALL")
_REGEX_REPLACE = ("REGEX", "REPLACE")
_STEM_LAST_ONLY = ("STEM", "LAST_ONLY")


class CMakeParseArguments(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "PARSE_ARGV": dict(
            front_positional_arguments=[
                "<N>",
                "<prefix>",
                "<options>",
                "<one_value_keywords>",
                "<multi_value_keywords>",
            ]
        ),
        None: dict(
            front_positional_arguments=[
                "<prefix>",
                "<options>",
                "<one_value_keywords>",
                "<multi_value_keywords>",
            ]
        ),
    }


class CMakePath(TwoWordKeywordIsolator, MultipleSignatureCommandInvocationDumper):
    two_words_keywords = [_EXTENSION_LAST_ONLY, _STEM_LAST_ONLY]
    customized_signatures = {
        # Decomposition
        "GET": {
            "front_positional_arguments": ["<path-var>"],
            "one_value_keywords": [
                "ROOT_NAME",
                "ROOT_DIRECTORY",
                "ROOT_PATH",
                "FILENAME",
                "EXTENSION",
                _EXTENSION_LAST_ONLY,
                "STEM",
                _STEM_LAST_ONLY,
                "RELATIVE_PART",
                "PARENT_PATH",
            ],
        },
        # Query
        "HAS_ROOT_NAME": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "HAS_ROOT_DIRECTORY": {
            "front_positional_arguments": ["<path-var>", "<out-var>"]
        },
        "HAS_ROOT_PATH": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "HAS_FILENAME": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "HAS_EXTENSION": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "HAS_STEM": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "HAS_RELATIVE_PATH": {
            "front_positional_arguments": ["<path-var>", "<out-var>"]
        },
        "HAS_PARENT_PATH": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "IS_ABSOLUTE": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "IS_RELATIVE": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
        "IS_PREFIX": {
            "front_positional_arguments": ["<path-var>", "<out-var>"],
            "back_positional_arguments": ["<out-var>"],
            "options": ["NORMALIZE"],
        },
        "COMPARE": {
            "front_positional_arguments": ["<input1>", "<OP>", "<input2>", "<out-var>"]
        },
        # Modification
        "SET": {
            "front_positional_arguments": ["<path-var>"],
            "back_positional_arguments": ["<input>"],
            "options": ["NORMALIZE"],
        },
        "APPEND": {
            "front_positional_arguments": ["<path-var>"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        "APPEND_STRING": {
            "front_positional_arguments": ["<path-var>"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        "REMOVE_FILENAME": {
            "front_positional_arguments": ["<path-var>"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        "REPLACE_FILENAME": {
            "front_positional_arguments": ["<path-var>", "<input>"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        "REMOVE_EXTENSION": {
            "front_positional_arguments": ["<path-var>"],
            "options": ["LAST_ONLY"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        "REPLACE_EXTENSION": {
            "front_positional_arguments": ["<path-var>"],
            "options": ["LAST_ONLY"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        # Generation
        "NORMAL_PATH": {
            "front_positional_arguments": ["<path-var>"],
            "one_value_keywords": ["OUTPUT_VARIABLE"],
        },
        "RELATIVE_PATH": {
            "front_positional_arguments": ["<path-var>"],
            "one_value_keywords": ["BASE_DIRECTORY", "OUTPUT_VARIABLE"],
        },
        "ABSOLUTE_PATH": {
            "front_positional_arguments": ["<path-var>"],
            "options": ["NORMALIZE"],
            "one_value_keywords": ["BASE_DIRECTORY", "OUTPUT_VARIABLE"],
        },
        # Native Conversion
        "NATIVE_PATH": {
            "front_positional_arguments": ["<path-var>"],
            "back_positional_arguments": ["<out-var>"],
            "options": ["NORMALIZE"],
        },
        "CONVERT": {
            "front_positional_arguments": ["<input>"],
            "options": ["NORMALIZE"],
            "one_value_keywords": ["TO_CMAKE_PATH_LIST", "TO_NATIVE_PATH_LIST"],
        },
        # Hashing
        "HASH": {
            "front_positional_arguments": ["<path-var>", "<out-var>"],
        },
    }


class CMakePolicy(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "VERSION": dict(front_positional_arguments=["<min>...<max>"]),
        "SET": dict(options=["OLD", "NEW"]),
        "GET": dict(back_positional_arguments=["<variable>"]),
        "PUSH": dict(),
        "POP": dict(),
    }


_GENERATE_OUTPUT = ("GENERATE", "OUTPUT")


class File(TwoWordKeywordIsolator, MultipleSignatureCommandInvocationDumper):
    two_words_keywords = [_GENERATE_OUTPUT]
    customized_signatures = {
        # Reading
        "READ": dict(
            front_positional_arguments=["<filename>", "<variable>"],
            options=["HEX"],
            one_value_keywords=["OFFSET", "LIMIT"],
        ),
        "STRINGS": dict(
            front_positional_arguments=["<filename>", "<variable>"],
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
        ),
        "MD5": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA1": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA224": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA256": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA384": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA512": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_224": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_256": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_384": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_512": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "TIMESTAMP": dict(
            front_positional_arguments=["<filename>", "<variable>", "<format>"],
            options=["UTC"],
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
                "POST_INCLUDE_FILES",
                "POST_EXCLUDE_FILES",
            ],
        ),
        # Writing
        "WRITE": dict(front_positional_arguments=["<filename>"]),
        "APPEND": dict(front_positional_arguments=["<filename>"]),
        _GENERATE_OUTPUT: dict(
            front_positional_arguments=["output-file"],
            options=["NO_SOURCE_PERMISSIONS", "USE_SOURCE_PERMISSIONS"],
            one_value_keywords=[
                "INPUT",
                "CONTENT",
                "CONDITION",
                "TARGET",
                "NEWLINE_STYLE",
            ],
            multi_value_keywords=["FILE_PERMISSIONS"],
        ),
        "CONFIGURE": dict(
            options=["ESCAPE_QUOTES", "@ONLY"],
            one_value_keywords=["OUTPUT", "CONTENT", "NEWLINE_STYLE"],
        ),
        # Filesystem
        "GLOB": dict(
            front_positional_arguments=["<variable>"],
            options=["CONFIGURE_DEPENDS"],
            one_value_keywords=["GLOB", "LIST_DIRECTORIES", "RELATIVE"],
        ),
        "GLOB_RECURSE": dict(
            front_positional_arguments=["<variable>"],
            options=["CONFIGURE_DEPENDS", "FOLLOW_SYMLINKS"],
            one_value_keywords=["GLOB_RECURSE", "LIST_DIRECTORIES", "RELATIVE"],
        ),
        "MAKE_DIRECTORY": dict(
            one_value_keywords=["RESULT"],
            multi_value_keywords=["MAKE_DIRECTORY"],
        ),
        "RENAME": dict(
            front_positional_arguments=["<oldname>", "<newname>"],
            options=["NO_REPLACE"],
            one_value_keywords=["RESULT"],
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
        "COPY_FILE": dict(
            front_positional_arguments=["<oldname>", "<newname>"],
            options=["ONLY_IF_DIFFERENT"],
            one_value_keywords=["RESULT"],
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
        "SIZE": dict(front_positional_arguments=["<filename>", "<variable>"]),
        "READ_SYMLINK": dict(front_positional_arguments=["<linkname>", "<variable>"]),
        "CREATE_LINK": dict(
            front_positional_arguments=["<original>", "<linkname>"],
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
        "REAL_PATH": dict(
            front_positional_arguments=["<path>", "<out-var>"],
            options=["EXPAND_TILDE"],
            one_value_keywords=["BASE_DIRECTORY"],
        ),
        "RELATIVE_PATH": dict(
            front_positional_arguments=["<variable>", "<directory>", "<file>"]
        ),
        "TO_CMAKE_PATH": dict(front_positional_arguments=["<path>", "<variable>"]),
        "TO_NATIVE_PATH": dict(front_positional_arguments=["<path>", "<variable>"]),
        # Transfer
        "DOWNLOAD": dict(
            front_positional_arguments=["<url>", "<file>"],
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
                "RANGE_START",
                "RANGE_END",
                "TLS_VERSION",
            ],
            multi_value_keywords=["DOWNLOAD"],
        ),
        "UPLOAD": dict(
            front_positional_arguments=["<file>", "<url>"],
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
                "TLS_VERSION",
            ],
            multi_value_keywords=["UPLOAD"],
        ),
        # Locking
        "LOCK": dict(
            front_positional_arguments=["<path>"],
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
                "WORKING_DIRECTORY",
            ],
            multi_value_keywords=["PATHS"],
        ),
        "ARCHIVE_EXTRACT": dict(
            options=["LIST_ONLY", "VERBOSE"],
            one_value_keywords=["INPUT", "DESTINATION"],
            multi_value_keywords=["PATTERNS"],
        ),
    }


class List(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        # Reading
        "LENGTH": dict(front_positional_arguments=["<list>", "<output variable>"]),
        "GET": dict(
            front_positional_arguments=["<list>"],
            back_positional_arguments=["<output variable>"],
        ),
        "JOIN": dict(
            front_positional_arguments=["<list>", "<glue", "<output variable>"]
        ),
        "SUBLIST": dict(
            front_positional_arguments=[
                "<list>",
                "<begin>",
                "<length>",
                "<out-var>",
            ],
        ),
        # Search
        "FIND": dict(
            front_positional_arguments=["<list>", "<value>", "<output variable>"]
        ),
        # Modification
        "APPEND": dict(front_positional_arguments=["<list>"]),
        "FILTER": dict(
            options=["INCLUDE", "EXCLUDE"], one_value_keywords=["FILTER", "REGEX"]
        ),
        "INSERT": dict(front_positional_arguments=["<list>", "<element_index>"]),
        "POP_BACK": dict(front_positional_arguments=["<list>"]),
        "POP_FRONT": dict(front_positional_arguments=["<list>"]),
        "PREPEND": dict(front_positional_arguments=["<list>"]),
        "REMOVE_ITEM": dict(front_positional_arguments=["<list>"]),
        "REMOVE_AT": dict(front_positional_arguments=["<list>"]),
        "REMOVE_DUPLICATES": dict(front_positional_arguments=["<list>"]),
        "TRANSFORM": dict(
            front_positional_arguments=["<list>"],
            one_value_keywords=["OUTPUT_VARIABLE", "TRANSFORM"],
            multi_value_keywords=[
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
        "REVERSE": dict(front_positional_arguments=["<list>"]),
        "SORT": dict(one_value_keywords=["SORT", "COMPARE", "CASE", "ORDER"]),
    }


class SetProperty(ArgumentAwareCommandInvocationDumper):
    options = ["GLOBAL", "APPEND", "APPEND_STRING"]
    multi_value_keywords = [
        "TARGET",
        "SOURCE",
        "INSTALL",
        "TEST",
        "CACHE",
        "PROPERTY",
        "TARGET_DIRECTORIES",
        "DIRECTORY",
    ]
    keyword_formatters = {"PROPERTY": "_format_property"}

    def _format_property(self, args):
        result = self._try_to_format_into_single_line(
            args, separator=" ", prefix="", postfix=""
        )
        if result is not None:
            return result

        name, *rest = args
        with self.indented():
            formatted_rest = "\n".join(map(self.visit, rest))
        return f"{self.visit(name)}\n{formatted_rest}"


class String(TwoWordKeywordIsolator, MultipleSignatureCommandInvocationDumper):
    two_words_keywords = [
        _REGEX_MATCH,
        _REGEX_MATCHALL,
        _REGEX_REPLACE,
        _COMPARE_LESS,
        _COMPARE_GREATER,
        _COMPARE_EQUAL,
        _COMPARE_NOTEQUAL,
        _COMPARE_LESS_EQUAL,
        _COMPARE_GREATER_EQUAL,
    ]
    customized_signatures = {
        # Search and Replace
        "FIND": dict(
            front_positional_arguments=["<string>", "<substring>", "<output variable>"],
            options=["REVERSE"],
        ),
        "REPLACE": dict(
            front_positional_arguments=[
                "<match_string>",
                "<replace_string>",
                "<output_variable>",
            ]
        ),
        # Regular Expressions
        _REGEX_MATCH: dict(
            front_positional_arguments=["<regular_expression>", "<output_variable>"]
        ),
        _REGEX_MATCHALL: dict(
            front_positional_arguments=["<regular_expression>", "<output_variable>"]
        ),
        _REGEX_REPLACE: dict(
            front_positional_arguments=[
                "<regular_expression>",
                "<replacement_expression>",
                "<output_variable>",
            ]
        ),
        # Manipulation
        "APPEND": dict(front_positional_arguments=["<string_variable>"]),
        "PREPEND": dict(front_positional_arguments=["<string_variable>"]),
        "CONCAT": dict(front_positional_arguments=["<output_variable>"]),
        "JOIN": dict(front_positional_arguments=["<glue>", "<output_variable>"]),
        "TOLOWER": dict(front_positional_arguments=["<string>", "<output_variable>"]),
        "TOUPPER": dict(front_positional_arguments=["<string>", "<output_variable>"]),
        "LENGTH": dict(front_positional_arguments=["<string>", "<output_variable>"]),
        "SUBSTRING": dict(
            front_positional_arguments=[
                "<string>",
                "<begin>",
                "<length>",
                "<output_variable>",
            ]
        ),
        "STRIP": dict(front_positional_arguments=["<string>", "<output_variable>"]),
        "GENEX_STRIP": dict(
            front_positional_arguments=["<string>", "<output_variable>"]
        ),
        "REPEAT": dict(
            front_positional_arguments=["<string>", "<count>", "<output_variable>"]
        ),
        # Comparison
        _COMPARE_LESS: dict(
            front_positional_arguments=["<string1>", "<string2>", "<output_variable>"]
        ),
        _COMPARE_GREATER: dict(
            front_positional_arguments=["<string1>", "<string2>", "<output_variable>"]
        ),
        _COMPARE_EQUAL: dict(
            front_positional_arguments=["<string1>", "<string2>", "<output_variable>"]
        ),
        _COMPARE_NOTEQUAL: dict(
            front_positional_arguments=["<string1>", "<string2>", "<output_variable>"]
        ),
        _COMPARE_LESS_EQUAL: dict(
            front_positional_arguments=["<string1>", "<string2>", "<output_variable>"]
        ),
        _COMPARE_GREATER_EQUAL: dict(
            front_positional_arguments=["<string1>", "<string2>", "<output_variable>"]
        ),
        # Hashing
        "MD5": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA1": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA224": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA256": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA384": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA512": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_224": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_256": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_384": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        "SHA3_512": dict(front_positional_arguments=["<output_variable>", "<input>"]),
        # Generation
        "ASCII": dict(
            back_positional_arguments=["<output_variable>"],
        ),
        "HEX": dict(front_positional_arguments=["<string>", "<output_variable>"]),
        "CONFIGURE": dict(
            front_positional_arguments=["<string>", "<output_variable>"],
            options=["@ONLY", "ESCAPE_QUOTES"],
        ),
        "MAKE_C_IDENTIFIER": dict(
            front_positional_arguments=["<string>", "<output_variable>"]
        ),
        "RANDOM": dict(one_value_keywords=["LENGTH", "ALPHABET", "RANDOM_SEED"]),
        "TIMESTAMP": dict(
            front_positional_arguments=["<filename>", "<variable>", "<format>"],
            options=["UTC"],
        ),
        "UUID": dict(
            front_positional_arguments=["<output_variable>"],
            options=["UPPER"],
            one_value_keywords=["NAMESPACE", "NAME", "TYPE"],
        ),
        # JSON
        "JSON": dict(
            front_positional_arguments=["<out-var>"],
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


scripting_command_mapping = {
    "block": {
        "inhibit_favour_expansion": True,
        "multi_value_keywords": ["SCOPE_FOR", "PROPAGATE"],
    },
    "cmake_host_system_information": {
        "two_words_keywords": [_QUERY_WINDOWS_REGISTRY],
        "one_value_keywords": [
            "RESULT",
            _QUERY_WINDOWS_REGISTRY,
            "VALUE_NAMES",
            "SUBKEYS",
            "VALUE",
            "VIEW",
            "SEPARATOR",
            "ERROR_VARIABLE",
        ],
        "multi_value_keywords": ["QUERY"],
    },
    "cmake_language": {
        "two_words_keywords": [_EVAL_CODE],
        "one_value_keywords": [
            "DIRECTORY",
            "ID",
            "ID_VAR",
            "GET_CALL_IDS",
            "GET_CALL",
            "SET_DEPENDENCY_PROVIDER",
            "GET_MESSAGE_LOG_LEVEL",
            "EXIT",
        ],
        "multi_value_keywords": [
            "DEFER",
            "CALL",
            "CANCEL_CALL",
            "SUPPORTED_METHODS",
            _EVAL_CODE,
        ],
    },
    "cmake_minimum_required": {
        "options": ["FATAL_ERROR"],
        "one_value_keywords": ["VERSION"],
    },
    "cmake_parse_arguments": CMakeParseArguments,
    "cmake_path": CMakePath,
    "cmake_pkg_config": {
        "options": ["REQUIRED", "EXACT", "QUIET"],
        "one_value_keywords": [
            "STRICTNESS",
            "ENV_MODE",
            "DISABLE_UNINSTALLED",
            "PC_SYSROOT_DIR",
            "TOP_BUILD_DIR",
            "ALLOW_SYSTEM_INCLUDES",
            "ALLOW_SYSTEM_LIBS",
        ],
        "multi_value_keywords": [
            "EXTRACT",
            "PC_LIBDIR",
            "PC_PATH",
            "SYSTEM_INCLUDE_DIRS",
            "SYSTEM_LIBRARY_DIRS",
        ],
    },
    "cmake_policy": CMakePolicy,
    "configure_file": {
        "front_positional_arguments": ["<input>", "<output>"],
        "options": [
            "COPYONLY",
            "ESCAPE_QUOTES",
            "@ONLY",
            "NO_SOURCE_PERMISSIONS",
            "USE_SOURCE_PERMISSIONS",
        ],
        "one_value_keywords": ["NEWLINE_STYLE"],
        "multi_value_keywords": ["FILE_PERMISSIONS"],
    },
    "elseif": ConditionSyntaxCommandInvocationDumper,
    "else": ConditionSyntaxCommandInvocationDumper,
    "endif": ConditionSyntaxCommandInvocationDumper,
    "endblock": {},
    "endforeach": {},
    "endfunction": {},
    "endmacro": {},
    "endwhile": ConditionSyntaxCommandInvocationDumper,
    "execute_process": {
        "options": [
            "OUTPUT_QUIET",
            "ERROR_QUIET",
            "OUTPUT_STRIP_TRAILING_WHITESPACE",
            "ERROR_STRIP_TRAILING_WHITESPACE",
            "ECHO_OUTPUT_VARIABLE",
            "ECHO_ERROR_VARIABLE",
        ],
        "one_value_keywords": [
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
        ],
        "multi_value_keywords": ["COMMAND"],
        "keyword_formatters": {"COMMAND": "_format_command_line"},
    },
    "file": File,
    "find_file": {
        "front_positional_arguments": ["<VAR>", "name"],
        "options": [
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
            "NO_CMAKE_INSTALL_PREFIX",
        ],
        "one_value_keywords": ["DOC", "ENV", "VALIDATOR"],
        "multi_value_keywords": ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"],
    },
    "find_library": {
        "front_positional_arguments": ["<VAR>", "name"],
        "options": [
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
            "NO_CMAKE_INSTALL_PREFIX",
        ],
        "one_value_keywords": ["DOC", "ENV", "VALIDATOR"],
        "multi_value_keywords": ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"],
    },
    "find_package": {
        "front_positional_arguments": ["<PackageName>", "<version>"],
        "options": [
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
            "NO_CMAKE_INSTALL_PREFIX",
            "GLOBAL",
        ],
        "multi_value_keywords": [
            "COMPONENTS",
            "OPTIONAL_COMPONENTS",
            "NAMES",
            "CONFIGS",
            "HINTS",
            "PATHS",
            "PATH_SUFFIXES",
            "REQUIRED",
        ],
    },
    "find_path": {
        "front_positional_arguments": ["<VAR>", "name"],
        "options": [
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
            "NO_CMAKE_INSTALL_PREFIX",
        ],
        "one_value_keywords": ["DOC", "ENV", "VALIDATOR"],
        "multi_value_keywords": ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"],
    },
    "find_program": {
        "front_positional_arguments": ["<VAR>", "name"],
        "options": [
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
            "NO_CMAKE_INSTALL_PREFIX",
        ],
        "one_value_keywords": ["DOC", "ENV", "VALIDATOR"],
        "multi_value_keywords": ["NAMES", "HINTS", "PATHS", "PATH_SUFFIXES"],
    },
    "foreach": {
        "inhibit_favour_expansion": True,
        "front_positional_arguments": ["<loop_var>"],
        "options": ["IN"],
        "multi_value_keywords": ["RANGE", "LISTS", "ITEMS", "ZIP_LISTS"],
    },
    "function": {
        "inhibit_favour_expansion": True,
        "front_positional_arguments": ["<name>"],
    },
    "get_cmake_property": {
        "front_positional_arguments": ["<var>", "<property>"],
    },
    "get_directory_property": {
        "front_positional_arguments": ["<variable>"],
        "one_value_keywords": ["DIRECTORY", "DEFINITION"],
    },
    "get_filename_component": {
        "front_positional_arguments": [
            "<var>",
            "<FileName>",
            "<mode>",
        ],
        "options": [
            "DIRECTORY",
            "NAME",
            "EXT",
            "NAME_WE",
            "LAST_EXT",
            "NAME_WLE",
            "PATH",
            "PROGRAM",
            "CACHE",
        ],
        "one_value_keywords": ["BASE_DIR", "PROGRAM_ARGS"],
    },
    "get_property": {
        "front_positional_arguments": ["<variable>"],
        "options": ["GLOBAL", "VARIABLE", "SET", "DEFINED", "BRIEF_DOCS", "FULL_DOCS"],
        "one_value_keywords": [
            "TARGET",
            "INSTALL",
            "TEST",
            "CACHE",
            "PROPERTY",
            "TARGET_DIRECTORY",
            "SOURCE",
        ],
        "multi_value_keywords": ["DIRECTORY"],
    },
    "get_source_file_property": {
        "one_value_keywords": ["DIRECTORY", "TARGET_DIRECTORY"],
    },
    "if": ConditionSyntaxCommandInvocationDumper,
    "include": {
        "front_positional_arguments": ["<file|module>"],
        "options": ["OPTIONAL", "NO_POLICY_SCOPE"],
        "one_value_keywords": ["RESULT_VARIABLE"],
    },
    "list": List,
    "macro": {
        "inhibit_favour_expansion": True,
        "front_positional_arguments": ["<name>"],
    },
    "mark_as_advanced": {
        "options": ["CLEAR", "FORCE"],
    },
    "math": {
        "front_positional_arguments": ["EXPR", "<variable>", "<expression>"],
        "one_value_keywords": ["OUTPUT_FORMAT"],
    },
    "message": {
        "options": [
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
            "CONFIGURE_LOG",
        ],
    },
    "option": {
        "front_positional_arguments": ["<variable>", "<help_text>", "<value>"],
    },
    "return": {
        "multi_value_keywords": ["PROPAGATE"],
    },
    "separate_arguments": {
        "front_positional_arguments": ["<variable>", "<mode>"],
        "options": ["PROGRAM", "SEPARATE_ARGS"],
    },
    "set_directory_properties": {
        "multi_value_keywords": ["PROPERTIES"],
        "keyword_formatters": {"PROPERTIES": "_format_keyword_with_pairs"},
    },
    "set_property": SetProperty,
    "set": {
        "front_positional_arguments": ["<variable>"],
        "options": ["PARENT_SCOPE", "FORCE"],
        "one_value_keywords": ["CACHE"],
    },
    "string": String,
    "unset": {
        "front_positional_arguments": ["<variable>"],
        "options": ["CACHE", "PARENT_SCOPE"],
    },
    "while": ConditionSyntaxCommandInvocationDumper,
}
