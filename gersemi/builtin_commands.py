# pylint: disable=too-many-lines
from typing import Iterable, List, Mapping
from gersemi.immutable import make_immutable
from gersemi.specializations.add_custom_target import add_custom_target
from gersemi.specializations.condition_syntax_command_invocation_dumper import (
    condition_syntax_commands,
)
from gersemi.specializations.set_property import set_property
from gersemi.keywords import AnyMatcher, KeywordMatcher
from gersemi.keyword_kind import KeywordFormatter


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
_GENERATE_OUTPUT = ("GENERATE", "OUTPUT")
_INCLUDES_DESTINATION = ("INCLUDES", "DESTINATION")
_FILE_SET_Any = ("FILE_SET", AnyMatcher())
_PATTERN_Any = ("PATTERN", AnyMatcher())
_REGEX_Any = ("REGEX", AnyMatcher())
_Install_TARGETS_kinds: List[KeywordMatcher] = [
    "ARCHIVE",
    "LIBRARY",
    "RUNTIME",
    "OBJECTS",
    "FRAMEWORK",
    "BUNDLE",
    "PUBLIC_HEADER",
    "PRIVATE_HEADER",
    "RESOURCE",
    _FILE_SET_Any,
    "CXX_MODULES_BMI",
]
_Install_TARGETS_artifact_option_group = {
    "options": ["OPTIONAL", "EXCLUDE_FROM_ALL", "NAMELINK_ONLY", "NAMELINK_SKIP"],
    "one_value_keywords": ["DESTINATION", "COMPONENT", "NAMELINK_COMPONENT"],
    "multi_value_keywords": ["PERMISSIONS", "CONFIGURATIONS"],
}
_Install_IMPORTED_RUNTIME_ARTIFACTS_kinds = [
    "LIBRARY",
    "RUNTIME",
    "FRAMEWORK",
    "BUNDLE",
]
_Install_DIRECTORY_kinds: List[KeywordMatcher] = [_PATTERN_Any, _REGEX_Any]
_Install_RUNTIME_DEPENDENCY_SET_kinds = ["LIBRARY", "RUNTIME", "FRAMEWORK"]
_debug_optimized_general: Mapping[KeywordMatcher, Iterable[KeywordMatcher]] = {
    "one_value_keywords": ["debug", "optimized", "general"]
}

_ExternalProject_Add_DownloadStep = {
    "one_value_keywords": {
        # Described in "Directory Options"
        "DOWNLOAD_DIR",
        #
        "URL_HASH",
        "URL_MD5",
        "DOWNLOAD_NAME",
        "DOWNLOAD_EXTRACT_TIMESTAMP",
        "DOWNLOAD_NO_EXTRACT",
        "DOWNLOAD_NO_PROGRESS",
        "TIMEOUT",
        "INACTIVITY_TIMEOUT",
        "HTTP_USERNAME",
        "HTTP_PASSWORD",
        "TLS_VERSION",
        "TLS_VERIFY",
        "TLS_CAINFO",
        "NETRC",
        "NETRC_FILE",
        "GIT_REPOSITORY",
        "GIT_TAG",
        "GIT_REMOTE_NAME",
        "GIT_SUBMODULES_RECURSE",
        "GIT_SHALLOW",
        "GIT_PROGRESS",
        "GIT_REMOTE_UPDATE_STRATEGY",
        "SVN_REPOSITORY",
        "SVN_REVISION",
        "SVN_USERNAME",
        "SVN_PASSWORD",
        "SVN_TRUST_CERT",
        "HG_REPOSITORY",
        "HG_TAG",
        "CVS_REPOSITORY",
        "CVS_MODULE",
        "CVS_TAG",
    },
    "multi_value_keywords": {
        "DOWNLOAD_COMMAND",
        "URL",
        "HTTP_HEADER",
        "GIT_SUBMODULES",
        "GIT_CONFIG",
    },
}
_ExternalProject_Add_UpdateStep = {
    "one_value_keywords": ["UPDATE_DISCONNECTED"],
    "multi_value_keywords": ["UPDATE_COMMAND"],
}
_ExternalProject_Add_PatchStep = {
    "one_value_keywords": [],
    "multi_value_keywords": ["PATCH_COMMAND"],
}

_target_sources_FILE_SET = {
    "multi_value_keywords": [_FILE_SET_Any],
    "sections": {
        _FILE_SET_Any: {
            "one_value_keywords": ["TYPE"],
            "multi_value_keywords": ["BASE_DIRS", "FILES"],
        }
    },
}

builtin_commands = {
    #### Legend
    #### (&): canonical name used different than in the documentation
    #
    # cmake-commands
    #
    ## Scripting Commands
    #
    "block": {
        "_inhibit_favour_expansion": True,
        "multi_value_keywords": ["SCOPE_FOR", "PROPAGATE"],
    },
    "break": {},
    "cmake_host_system_information": {
        "_two_words_keywords": [_QUERY_WINDOWS_REGISTRY],
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
        "_two_words_keywords": [_EVAL_CODE],
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
    "cmake_parse_arguments": {
        "signatures": {
            "PARSE_ARGV": {
                "front_positional_arguments": [
                    "<N>",
                    "<prefix>",
                    "<options>",
                    "<one_value_keywords>",
                    "<multi_value_keywords>",
                ]
            },
            None: {
                "front_positional_arguments": [
                    "<prefix>",
                    "<options>",
                    "<one_value_keywords>",
                    "<multi_value_keywords>",
                ]
            },
        },
    },
    "cmake_path": {
        "_two_words_keywords": [_EXTENSION_LAST_ONLY, _STEM_LAST_ONLY],
        "signatures": {
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
            "HAS_ROOT_NAME": {
                "front_positional_arguments": ["<path-var>", "<out-var>"]
            },
            "HAS_ROOT_DIRECTORY": {
                "front_positional_arguments": ["<path-var>", "<out-var>"]
            },
            "HAS_ROOT_PATH": {
                "front_positional_arguments": ["<path-var>", "<out-var>"]
            },
            "HAS_FILENAME": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
            "HAS_EXTENSION": {
                "front_positional_arguments": ["<path-var>", "<out-var>"]
            },
            "HAS_STEM": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
            "HAS_RELATIVE_PATH": {
                "front_positional_arguments": ["<path-var>", "<out-var>"]
            },
            "HAS_PARENT_PATH": {
                "front_positional_arguments": ["<path-var>", "<out-var>"]
            },
            "IS_ABSOLUTE": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
            "IS_RELATIVE": {"front_positional_arguments": ["<path-var>", "<out-var>"]},
            "IS_PREFIX": {
                "front_positional_arguments": ["<path-var>", "<out-var>"],
                "back_positional_arguments": ["<out-var>"],
                "options": ["NORMALIZE"],
            },
            "COMPARE": {
                "front_positional_arguments": [
                    "<input1>",
                    "<OP>",
                    "<input2>",
                    "<out-var>",
                ]
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
        },
    },
    "cmake_pkg_config": {
        "signatures": {
            "EXTRACT": {
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
            "POPULATE": {
                "options": ["REQUIRED", "EXACT", "QUIET"],
                "one_value_keywords": [
                    "PREFIX",
                    "STRICTNESS",
                    "ENV_MODE",
                    "DISABLE_UNINSTALLED",
                    "PC_SYSROOT_DIR",
                    "TOP_BUILD_DIR",
                ],
                "multi_value_keywords": [
                    "POPULATE",
                    "BIND_PC_REQUIRES",
                    "PC_LIBDIR",
                    "PC_PATH",
                ],
            },
            "IMPORT": {
                "options": ["REQUIRED", "EXACT", "QUIET"],
                "one_value_keywords": [
                    "NAME",
                    "PREFIX",
                    "STRICTNESS",
                    "ENV_MODE",
                    "DISABLE_UNINSTALLED",
                    "PC_SYSROOT_DIR",
                    "TOP_BUILD_DIR",
                ],
                "multi_value_keywords": [
                    "IMPORT",
                    "BIND_PC_REQUIRES",
                    "PC_LIBDIR",
                    "PC_PATH",
                ],
            },
        }
    },
    "cmake_policy": {
        "signatures": {
            "VERSION": {"front_positional_arguments": ["<min>...<max>"]},
            "SET": {"options": ["OLD", "NEW"]},
            "GET": {"back_positional_arguments": ["<variable>"]},
            "PUSH": {},
            "POP": {},
        },
    },
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
    "continue": {},
    **condition_syntax_commands,
    "endblock": {},
    "endforeach": {},
    "endfunction": {},
    "endmacro": {},
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
        "keyword_formatters": {"COMMAND": KeywordFormatter.CommandLine},
    },
    "file": {
        "_two_words_keywords": [_GENERATE_OUTPUT],
        "signatures": {
            # Reading
            "READ": {
                "front_positional_arguments": ["<filename>", "<variable>"],
                "options": ["HEX"],
                "one_value_keywords": ["OFFSET", "LIMIT"],
            },
            "STRINGS": {
                "front_positional_arguments": ["<filename>", "<variable>"],
                "options": ["NEWLINE_CONSUME", "NO_HEX_CONVERSION"],
                "one_value_keywords": [
                    "LENGTH_MAXIMUM",
                    "LENGTH_MINIMUM",
                    "LIMIT_COUNT",
                    "LIMIT_INPUT",
                    "LIMIT_OUTPUT",
                    "REGEX",
                    "ENCODING",
                ],
            },
            "MD5": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA1": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA224": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA256": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA384": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA512": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA3_224": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "SHA3_256": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "SHA3_384": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "SHA3_512": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "TIMESTAMP": {
                "front_positional_arguments": ["<filename>", "<variable>", "<format>"],
                "options": ["UTC"],
            },
            "GET_RUNTIME_DEPENDENCIES": {
                "one_value_keywords": [
                    "RESOLVED_DEPENDENCIES_VAR",
                    "UNRESOLVED_DEPENDENCIES_VAR",
                    "CONFLICTING_DEPENDENCIES_PREFIX",
                    "BUNDLE_EXECUTABLE",
                ],
                "multi_value_keywords": [
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
            },
            # Writing
            "WRITE": {"front_positional_arguments": ["<filename>"]},
            "APPEND": {"front_positional_arguments": ["<filename>"]},
            _GENERATE_OUTPUT: {
                "front_positional_arguments": ["output-file"],
                "options": ["NO_SOURCE_PERMISSIONS", "USE_SOURCE_PERMISSIONS"],
                "one_value_keywords": [
                    "INPUT",
                    "CONTENT",
                    "CONDITION",
                    "TARGET",
                    "NEWLINE_STYLE",
                ],
                "multi_value_keywords": ["FILE_PERMISSIONS"],
            },
            "CONFIGURE": {
                "options": ["ESCAPE_QUOTES", "@ONLY"],
                "one_value_keywords": ["OUTPUT", "CONTENT", "NEWLINE_STYLE"],
            },
            # Filesystem
            "GLOB": {
                "front_positional_arguments": ["<variable>"],
                "options": ["CONFIGURE_DEPENDS"],
                "one_value_keywords": ["GLOB", "LIST_DIRECTORIES", "RELATIVE"],
            },
            "GLOB_RECURSE": {
                "front_positional_arguments": ["<variable>"],
                "options": ["CONFIGURE_DEPENDS", "FOLLOW_SYMLINKS"],
                "one_value_keywords": ["GLOB_RECURSE", "LIST_DIRECTORIES", "RELATIVE"],
            },
            "MAKE_DIRECTORY": {
                "one_value_keywords": ["RESULT"],
                "multi_value_keywords": ["MAKE_DIRECTORY"],
            },
            "RENAME": {
                "front_positional_arguments": ["<oldname>", "<newname>"],
                "options": ["NO_REPLACE"],
                "one_value_keywords": ["RESULT"],
            },
            "COPY": {
                "options": [
                    "NO_SOURCE_PERMISSIONS",
                    "USE_SOURCE_PERMISSIONS",
                    "FOLLOW_SYMLINK_CHAIN",
                    "FILES_MATCHING",
                    "EXCLUDE",
                ],
                "one_value_keywords": ["DESTINATION", "PATTERN", "REGEX"],
                "multi_value_keywords": [
                    "COPY",
                    "FILE_PERMISSIONS",
                    "DIRECTORY_PERMISSIONS",
                    "PERMISSIONS",
                ],
            },
            "COPY_FILE": {
                "front_positional_arguments": ["<oldname>", "<newname>"],
                "options": ["ONLY_IF_DIFFERENT"],
                "one_value_keywords": ["RESULT"],
            },
            "INSTALL": {
                "options": [
                    "NO_SOURCE_PERMISSIONS",
                    "USE_SOURCE_PERMISSIONS",
                    "FOLLOW_SYMLINK_CHAIN",
                    "FILES_MATCHING",
                    "EXCLUDE",
                ],
                "one_value_keywords": ["DESTINATION", "PATTERN", "REGEX"],
                "multi_value_keywords": [
                    "INSTALL",
                    "FILE_PERMISSIONS",
                    "DIRECTORY_PERMISSIONS",
                    "PERMISSIONS",
                ],
            },
            "SIZE": {"front_positional_arguments": ["<filename>", "<variable>"]},
            "READ_SYMLINK": {
                "front_positional_arguments": ["<linkname>", "<variable>"]
            },
            "CREATE_LINK": {
                "front_positional_arguments": ["<original>", "<linkname>"],
                "options": ["COPY_ON_ERROR", "SYMBOLIC"],
                "one_value_keywords": ["RESULT"],
                "multi_value_keywords": ["CREATE_LINK"],
            },
            "CHMOD": {
                "multi_value_keywords": [
                    "PERMISSIONS",
                    "FILE_PERMISSIONS",
                    "DIRECTORY_PERMISSIONS",
                ]
            },
            "CHMOD_RECURSE": {
                "multi_value_keywords": [
                    "PERMISSIONS",
                    "FILE_PERMISSIONS",
                    "DIRECTORY_PERMISSIONS",
                ]
            },
            # Path Conversion
            "REAL_PATH": {
                "front_positional_arguments": ["<path>", "<out-var>"],
                "options": ["EXPAND_TILDE"],
                "one_value_keywords": ["BASE_DIRECTORY"],
            },
            "RELATIVE_PATH": {
                "front_positional_arguments": ["<variable>", "<directory>", "<file>"]
            },
            "TO_CMAKE_PATH": {"front_positional_arguments": ["<path>", "<variable>"]},
            "TO_NATIVE_PATH": {"front_positional_arguments": ["<path>", "<variable>"]},
            # Transfer
            "DOWNLOAD": {
                "front_positional_arguments": ["<url>", "<file>"],
                "options": ["SHOW_PROGRESS"],
                "one_value_keywords": [
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
                "multi_value_keywords": ["DOWNLOAD"],
            },
            "UPLOAD": {
                "front_positional_arguments": ["<file>", "<url>"],
                "options": ["SHOW_PROGRESS"],
                "one_value_keywords": [
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
                "multi_value_keywords": ["UPLOAD"],
            },
            # Locking
            "LOCK": {
                "front_positional_arguments": ["<path>"],
                "options": ["DIRECTORY", "RELEASE"],
                "one_value_keywords": ["LOCK", "GUARD", "RESULT_VARIABLE", "TIMEOUT"],
            },
            # Archiving
            "ARCHIVE_CREATE": {
                "options": ["VERBOSE"],
                "one_value_keywords": [
                    "OUTPUT",
                    "FORMAT",
                    "COMPRESSION",
                    "COMPRESSION_LEVEL",
                    "MTIME",
                    "WORKING_DIRECTORY",
                ],
                "multi_value_keywords": ["PATHS"],
            },
            "ARCHIVE_EXTRACT": {
                "options": ["LIST_ONLY", "VERBOSE"],
                "one_value_keywords": ["INPUT", "DESTINATION"],
                "multi_value_keywords": ["PATTERNS"],
            },
            "REMOVE": {},
            "REMOVE_RECURSE": {},
            "TOUCH": {},
            "TOUCH_NOCREATE": {},
        },
    },
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
        "_inhibit_favour_expansion": True,
        "front_positional_arguments": ["<loop_var>"],
        "options": ["IN"],
        "multi_value_keywords": ["RANGE", "LISTS", "ITEMS", "ZIP_LISTS"],
    },
    "function": {
        "_inhibit_favour_expansion": True,
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
    "include": {
        "front_positional_arguments": ["<file|module>"],
        "options": ["OPTIONAL", "NO_POLICY_SCOPE"],
        "one_value_keywords": ["RESULT_VARIABLE"],
    },
    "include_guard": {},
    "list": {
        "signatures": {
            # Reading
            "LENGTH": {"front_positional_arguments": ["<list>", "<output variable>"]},
            "GET": {
                "front_positional_arguments": ["<list>"],
                "back_positional_arguments": ["<output variable>"],
            },
            "JOIN": {
                "front_positional_arguments": ["<list>", "<glue", "<output variable>"]
            },
            "SUBLIST": {
                "front_positional_arguments": [
                    "<list>",
                    "<begin>",
                    "<length>",
                    "<out-var>",
                ]
            },
            # Search
            "FIND": {
                "front_positional_arguments": ["<list>", "<value>", "<output variable>"]
            },
            # Modification
            "APPEND": {"front_positional_arguments": ["<list>"]},
            "FILTER": {
                "options": ["INCLUDE", "EXCLUDE"],
                "one_value_keywords": ["FILTER", "REGEX"],
            },
            "INSERT": {"front_positional_arguments": ["<list>", "<element_index>"]},
            "POP_BACK": {"front_positional_arguments": ["<list>"]},
            "POP_FRONT": {"front_positional_arguments": ["<list>"]},
            "PREPEND": {"front_positional_arguments": ["<list>"]},
            "REMOVE_ITEM": {"front_positional_arguments": ["<list>"]},
            "REMOVE_AT": {"front_positional_arguments": ["<list>"]},
            "REMOVE_DUPLICATES": {"front_positional_arguments": ["<list>"]},
            "TRANSFORM": {
                "front_positional_arguments": ["<list>"],
                "one_value_keywords": ["OUTPUT_VARIABLE", "TRANSFORM"],
                "multi_value_keywords": [
                    "APPEND",
                    "PREPEND",
                    "TOLOWER",
                    "TOUPPER",
                    "STRIP",
                    "GENEX_STRIP",
                    "REPLACE",
                ],
            },
            # Ordering
            "REVERSE": {"front_positional_arguments": ["<list>"]},
            "SORT": {"one_value_keywords": ["SORT", "COMPARE", "CASE", "ORDER"]},
        },
    },
    "macro": {
        "_inhibit_favour_expansion": True,
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
        "keyword_formatters": {"PROPERTIES": KeywordFormatter.Pairs},
    },
    **set_property,
    "set": {
        "front_positional_arguments": ["<variable>"],
        "options": ["PARENT_SCOPE", "FORCE"],
        "one_value_keywords": ["CACHE"],
    },
    "string": {
        "_two_words_keywords": [
            _REGEX_MATCH,
            _REGEX_MATCHALL,
            _REGEX_REPLACE,
            _COMPARE_LESS,
            _COMPARE_GREATER,
            _COMPARE_EQUAL,
            _COMPARE_NOTEQUAL,
            _COMPARE_LESS_EQUAL,
            _COMPARE_GREATER_EQUAL,
        ],
        "signatures": {
            # Search and Replace
            "FIND": {
                "front_positional_arguments": [
                    "<string>",
                    "<substring>",
                    "<output variable>",
                ],
                "options": ["REVERSE"],
            },
            "REPLACE": {
                "front_positional_arguments": [
                    "<match_string>",
                    "<replace_string>",
                    "<output_variable>",
                ]
            },
            # Regular Expressions
            _REGEX_MATCH: {
                "front_positional_arguments": [
                    "<regular_expression>",
                    "<output_variable>",
                ]
            },
            _REGEX_MATCHALL: {
                "front_positional_arguments": [
                    "<regular_expression>",
                    "<output_variable>",
                ]
            },
            _REGEX_REPLACE: {
                "front_positional_arguments": [
                    "<regular_expression>",
                    "<replacement_expression>",
                    "<output_variable>",
                ]
            },
            # Manipulation
            "APPEND": {"front_positional_arguments": ["<string_variable>"]},
            "PREPEND": {"front_positional_arguments": ["<string_variable>"]},
            "CONCAT": {"front_positional_arguments": ["<output_variable>"]},
            "JOIN": {"front_positional_arguments": ["<glue>", "<output_variable>"]},
            "TOLOWER": {
                "front_positional_arguments": ["<string>", "<output_variable>"]
            },
            "TOUPPER": {
                "front_positional_arguments": ["<string>", "<output_variable>"]
            },
            "LENGTH": {"front_positional_arguments": ["<string>", "<output_variable>"]},
            "SUBSTRING": {
                "front_positional_arguments": [
                    "<string>",
                    "<begin>",
                    "<length>",
                    "<output_variable>",
                ]
            },
            "STRIP": {"front_positional_arguments": ["<string>", "<output_variable>"]},
            "GENEX_STRIP": {
                "front_positional_arguments": ["<string>", "<output_variable>"]
            },
            "REPEAT": {
                "front_positional_arguments": [
                    "<string>",
                    "<count>",
                    "<output_variable>",
                ]
            },
            # Comparison
            _COMPARE_LESS: {
                "front_positional_arguments": [
                    "<string1>",
                    "<string2>",
                    "<output_variable>",
                ]
            },
            _COMPARE_GREATER: {
                "front_positional_arguments": [
                    "<string1>",
                    "<string2>",
                    "<output_variable>",
                ]
            },
            _COMPARE_EQUAL: {
                "front_positional_arguments": [
                    "<string1>",
                    "<string2>",
                    "<output_variable>",
                ]
            },
            _COMPARE_NOTEQUAL: {
                "front_positional_arguments": [
                    "<string1>",
                    "<string2>",
                    "<output_variable>",
                ]
            },
            _COMPARE_LESS_EQUAL: {
                "front_positional_arguments": [
                    "<string1>",
                    "<string2>",
                    "<output_variable>",
                ]
            },
            _COMPARE_GREATER_EQUAL: {
                "front_positional_arguments": [
                    "<string1>",
                    "<string2>",
                    "<output_variable>",
                ]
            },
            # Hashing
            "MD5": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA1": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA224": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA256": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA384": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA512": {"front_positional_arguments": ["<output_variable>", "<input>"]},
            "SHA3_224": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "SHA3_256": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "SHA3_384": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            "SHA3_512": {
                "front_positional_arguments": ["<output_variable>", "<input>"]
            },
            # Generation
            "ASCII": {"back_positional_arguments": ["<output_variable>"]},
            "HEX": {"front_positional_arguments": ["<string>", "<output_variable>"]},
            "CONFIGURE": {
                "front_positional_arguments": ["<string>", "<output_variable>"],
                "options": ["@ONLY", "ESCAPE_QUOTES"],
            },
            "MAKE_C_IDENTIFIER": {
                "front_positional_arguments": ["<string>", "<output_variable>"]
            },
            "RANDOM": {"one_value_keywords": ["LENGTH", "ALPHABET", "RANDOM_SEED"]},
            "TIMESTAMP": {
                "front_positional_arguments": ["<filename>", "<variable>", "<format>"],
                "options": ["UTC"],
            },
            "UUID": {
                "front_positional_arguments": ["<output_variable>"],
                "options": ["UPPER"],
                "one_value_keywords": ["NAMESPACE", "NAME", "TYPE"],
            },
            # JSON
            "JSON": {
                "front_positional_arguments": ["<out-var>"],
                "one_value_keywords": [
                    "ERROR_VARIABLE",
                    "GET",
                    "TYPE",
                    "MEMBER",
                    "LENGTH",
                    "REMOVE",
                    "SET",
                ],
                "multi_value_keywords": ["EQUAL"],
            },
        },
    },
    "site_name": {},
    "unset": {
        "front_positional_arguments": ["<variable>"],
        "options": ["CACHE", "PARENT_SCOPE"],
    },
    "variable_watch": {},
    #
    ## Project Commands
    #
    "add_compile_definitions": {},
    "add_compile_options": {},
    "add_custom_command": {
        "signatures": {
            "OUTPUT": {
                "options": [
                    "VERBATIM",
                    "APPEND",
                    "USES_TERMINAL",
                    "COMMAND_EXPAND_LISTS",
                    "DEPENDS_EXPLICIT_ONLY",
                    "CODEGEN",
                ],
                "one_value_keywords": [
                    "MAIN_DEPENDENCY",
                    "WORKING_DIRECTORY",
                    "COMMENT",
                    "DEPFILE",
                    "JOB_POOL",
                    "JOB_SERVER_AWARE",
                ],
                "multi_value_keywords": [
                    "OUTPUT",
                    "COMMAND",
                    "ARGS",
                    "DEPENDS",
                    "BYPRODUCTS",
                    "IMPLICIT_DEPENDS",
                    "OUTPUT",
                ],
                "keyword_formatters": {
                    "COMMAND": KeywordFormatter.CommandLine,
                    "ARGS": KeywordFormatter.CommandLine,
                },
            },
            "TARGET": {
                "options": [
                    "PRE_BUILD",
                    "PRE_LINK",
                    "POST_BUILD",
                    "VERBATIM",
                    "USES_TERMINAL",
                    "COMMAND_EXPAND_LISTS",
                ],
                "one_value_keywords": [
                    "TARGET",
                    "WORKING_DIRECTORY",
                    "COMMENT",
                    "TARGET",
                ],
                "multi_value_keywords": ["COMMAND", "ARGS", "BYPRODUCTS"],
                "keyword_formatters": {
                    "COMMAND": KeywordFormatter.CommandLine,
                    "ARGS": KeywordFormatter.CommandLine,
                },
            },
        },
    },
    **add_custom_target,
    "add_definitions": {},
    "add_dependencies": {
        "front_positional_arguments": ["<target>"],
    },
    "add_executable": {
        "_two_words_keywords": [("IMPORTED", "GLOBAL")],
        "front_positional_arguments": ["<name>"],
        "options": [
            "WIN32",
            "MACOSX_BUNDLE",
            "EXCLUDE_FROM_ALL",
            "IMPORTED",
            ("IMPORTED", "GLOBAL"),
        ],
        "one_value_keywords": ["ALIAS"],
    },
    "add_library": {
        "_two_words_keywords": [("IMPORTED", "GLOBAL")],
        "front_positional_arguments": ["<name>"],
        "options": [
            "STATIC",
            "SHARED",
            "MODULE",
            "EXCLUDE_FROM_ALL",
            "OBJECT",
            "IMPORTED",
            ("IMPORTED", "GLOBAL"),
            "UNKNOWN",
            "INTERFACE",
        ],
        "one_value_keywords": ["ALIAS"],
    },
    "add_link_options": {},
    "add_subdirectory": {
        "front_positional_arguments": ["source_dir", "binary_dir"],
        "options": ["EXCLUDE_FROM_ALL", "SYSTEM"],
    },
    "add_test": {
        "front_positional_arguments": ["<name>", "<command>"],
        "options": ["COMMAND_EXPAND_LISTS"],
        "one_value_keywords": ["NAME", "WORKING_DIRECTORY"],
        "multi_value_keywords": ["COMMAND", "CONFIGURATIONS"],
        "keyword_formatters": {"COMMAND": KeywordFormatter.CommandLine},
    },
    "aux_source_directory": {},
    "build_command": {
        "front_positional_arguments": ["<variable>"],
        "one_value_keywords": [
            "CONFIGURATION",
            "TARGET",
            "PROJECT_NAME",
            "PARALLEL_LEVEL",
        ],
    },
    "cmake_file_api": {
        "signatures": {
            "QUERY": {
                "options": ["QUERY"],
                "one_value_keywords": ["API_VERSION"],
                "multi_value_keywords": [
                    "CODEMODEL",
                    "CACHE",
                    "CMAKEFILES",
                    "TOOLCHAINS",
                ],
            },
        },
    },
    "create_test_sourcelist": {
        "front_positional_arguments": ["sourceListName", "driverName"],
        "one_value_keywords": ["EXTRA_INCLUDE", "FUNCTION"],
    },
    "define_property": {
        "options": [
            "GLOBAL",
            "DIRECTORY",
            "TARGET",
            "SOURCE",
            "TEST",
            "VARIABLE",
            "CACHED_VARIABLE",
            "INHERITED",
        ],
        "one_value_keywords": ["PROPERTY", "INITIALIZE_FROM_VARIABLE"],
        "multi_value_keywords": ["BRIEF_DOCS", "FULL_DOCS"],
    },
    "enable_language": {},
    "enable_testing": {},
    "export": {
        "signatures": {
            "EXPORT": {
                "options": ["EXPORT_PACKAGE_DEPENDENCIES"],
                "one_value_keywords": ["EXPORT", "NAMESPACE", "FILE"],
            },
            "TARGETS": {
                "options": ["APPEND", "EXPORT_LINK_INTERFACE_LIBRARIES"],
                "one_value_keywords": ["NAMESPACE", "FILE", "ANDROID_MK"],
                "multi_value_keywords": ["TARGETS"],
            },
            "PACKAGE": {"one_value_keywords": ["PACKAGE"]},
            "SETUP": {
                "one_value_keywords": ["SETUP"],
                "multi_value_keywords": ["PACKAGE_DEPENDENCY", "TARGET"],
                "sections": {
                    "PACKAGE_DEPENDENCY": {
                        "front_positional_arguments": ["<dep>"],
                        "one_value_keywords": ["ENABLED"],
                        "multi_value_keywords": ["EXTRA_ARGS"],
                    },
                    "TARGET": {
                        "front_positional_arguments": ["<target>"],
                        "one_value_keywords": ["XCFRAMEWORK_LOCATION"],
                    },
                },
            },
        },
    },
    "fltk_wrap_ui": {
        "front_positional_arguments": ["resultingLibraryName"],
    },
    "get_source_file_property": {
        "front_positional_arguments": ["<variable>", "<file>"],
        "back_positional_arguments": ["<property>"],
        "one_value_keywords": ["DIRECTORY", "TARGET_DIRECTORY"],
    },
    "get_target_property": {
        "front_positional_arguments": ["<VAR>", "target", "property"],
    },
    "get_test_property": {
        "front_positional_arguments": ["test", "property"],
        "one_value_keywords": ["DIRECTORY"],
    },
    "include_directories": {
        "options": ["AFTER", "BEFORE", "SYSTEM"],
    },
    "include_external_msproject": {
        "front_positional_arguments": ["projectname", "location"],
        "one_value_keywords": ["TYPE", "GUID", "PLATFORM"],
    },
    "include_regular_expression": {},
    "install": {
        "_two_words_keywords": [
            _INCLUDES_DESTINATION,
            _FILE_SET_Any,
            _PATTERN_Any,
            _REGEX_Any,
        ],
        "signatures": {
            "TARGETS": {
                "sections": {
                    kind: _Install_TARGETS_artifact_option_group
                    for kind in _Install_TARGETS_kinds
                },
                "options": _Install_TARGETS_artifact_option_group["options"],
                "one_value_keywords": [
                    *_Install_TARGETS_artifact_option_group["one_value_keywords"],
                    "EXPORT",
                    "RUNTIME_DEPENDENCY_SET",
                ],
                "multi_value_keywords": [
                    *_Install_TARGETS_artifact_option_group["multi_value_keywords"],
                    "TARGETS",
                    _INCLUDES_DESTINATION,
                    "RUNTIME_DEPENDENCIES",
                    *_Install_TARGETS_kinds,
                ],
            },
            "FILES": {
                "options": ["OPTIONAL", "EXCLUDE_FROM_ALL"],
                "one_value_keywords": ["TYPE", "DESTINATION", "COMPONENT", "RENAME"],
                "multi_value_keywords": ["FILES", "PERMISSIONS", "CONFIGURATIONS"],
            },
            "PROGRAMS": {
                "options": ["OPTIONAL", "EXCLUDE_FROM_ALL"],
                "one_value_keywords": ["TYPE", "DESTINATION", "COMPONENT", "RENAME"],
                "multi_value_keywords": ["PROGRAMS", "PERMISSIONS", "CONFIGURATIONS"],
            },
            "DIRECTORY": {
                "sections": {
                    kind: {
                        "options": ["EXCLUDE"],
                        "multi_value_keywords": ["PERMISSIONS"],
                    }
                    for kind in _Install_DIRECTORY_kinds
                },
                "options": [
                    "USE_SOURCE_PERMISSIONS",
                    "OPTIONAL",
                    "MESSAGE_NEVER",
                    "EXCLUDE_FROM_ALL",
                    "FILES_MATCHING",
                    "EXCLUDE_EMPTY_DIRECTORIES",
                ],
                "one_value_keywords": ["TYPE", "DESTINATION", "COMPONENT"],
                "multi_value_keywords": [
                    "DIRECTORY",
                    "FILE_PERMISSIONS",
                    "DIRECTORY_PERMISSIONS",
                    "CONFIGURATIONS",
                    *_Install_DIRECTORY_kinds,
                ],
            },
            "SCRIPT": {
                "options": ["EXCLUDE_FROM_ALL", "ALL_COMPONENTS"],
                "one_value_keywords": ["SCRIPT", "COMPONENT"],
            },
            "CODE": {
                "options": ["EXCLUDE_FROM_ALL", "ALL_COMPONENTS"],
                "one_value_keywords": ["CODE", "COMPONENT"],
            },
            "EXPORT": {
                "options": [
                    "EXPORT_LINK_INTERFACE_LIBRARIES",
                    "EXCLUDE_FROM_ALL",
                    "EXPORT_PACKAGE_DEPENDENCIES",
                ],
                "one_value_keywords": [
                    "EXPORT",
                    "DESTINATION",
                    "NAMESPACE",
                    "FILE",
                    "COMPONENT",
                ],
                "multi_value_keywords": ["PERMISSIONS", "CONFIGURATIONS"],
            },
            "EXPORT_ANDROID_MK": {
                "options": ["EXPORT_LINK_INTERFACE_LIBRARIES", "EXCLUDE_FROM_ALL"],
                "one_value_keywords": [
                    "EXPORT_ANDROID_MK",
                    "DESTINATION",
                    "NAMESPACE",
                    "FILE",
                    "COMPONENT",
                ],
                "multi_value_keywords": ["PERMISSIONS", "CONFIGURATIONS"],
            },
            "IMPORTED_RUNTIME_ARTIFACTS": {
                "sections": {
                    kind: {
                        "options": ["OPTIONAL", "EXCLUDE_FROM_ALL"],
                        "one_value_keywords": ["DESTINATION", "COMPONENT"],
                        "multi_value_keywords": ["PERMISSIONS", "CONFIGURATIONS"],
                    }
                    for kind in _Install_IMPORTED_RUNTIME_ARTIFACTS_kinds
                },
                "one_value_keywords": ["RUNTIME_DEPENDENCY_SET"],
                "multi_value_keywords": [
                    "IMPORTED_RUNTIME_ARTIFACTS",
                    *_Install_IMPORTED_RUNTIME_ARTIFACTS_kinds,
                ],
            },
            "RUNTIME_DEPENDENCY_SET": {
                "sections": {
                    kind: {
                        "options": ["OPTIONAL", "EXCLUDE_FROM_ALL"],
                        "one_value_keywords": [
                            "DESTINATION",
                            "COMPONENT",
                            "NAMELINK_COMPONENT",
                        ],
                        "multi_value_keywords": ["PERMISSIONS", "CONFIGURATIONS"],
                    }
                    for kind in _Install_RUNTIME_DEPENDENCY_SET_kinds
                },
                "multi_value_keywords": [
                    "PRE_INCLUDE_REGEXES",
                    "PRE_EXCLUDE_REGEXES",
                    "POST_INCLUDE_REGEXES",
                    "POST_EXCLUDE_REGEXES",
                    "POST_INCLUDE_FILES",
                    "POST_EXCLUDE_FILES",
                    "DIRECTORIES",
                    "RUNTIME_DEPENDENCY_SET",
                    *_Install_RUNTIME_DEPENDENCY_SET_kinds,
                ],
            },
            "PACKAGE_INFO": {
                "sections": {
                    "VERSION": {
                        "one_value_keywords": ["COMPAT_VERSION", "VERSION_SCHEMA"]
                    },
                },
                "options": ["LOWER_CASE_FILE", "EXCLUDE_FROM_ALL"],
                "one_value_keywords": [
                    "PACKAGE_INFO",
                    "EXPORT",
                    "APPENDIX",
                    "DESTINATION",
                    "COMPONENT",
                ],
                "multi_value_keywords": [
                    "VERSION",
                    "DEFAULT_TARGETS",
                    "DEFAULT_CONFIGURATIONS",
                    "PERMISSIONS",
                    "CONFIGURATIONS",
                ],
            },
        },
    },
    "link_directories": {
        "options": ["AFTER", "BEFORE"],
    },
    "link_libraries": {
        "one_value_keywords": ["debug", "optimized", "general"],
    },
    "load_cache": {
        "front_positional_arguments": ["pathToBuildDirectory"],
        "one_value_keywords": ["READ_WITH_PREFIX"],
        "multi_value_keywords": ["EXCLUDE", "INCLUDE_INTERNALS"],
    },
    "project": {
        "front_positional_arguments": ["<PROJECT-NAME>"],
        "one_value_keywords": [
            "VERSION",
            "DESCRIPTION",
            "HOMEPAGE_URL",
            "COMPAT_VERSION",
        ],
        "multi_value_keywords": ["LANGUAGES"],
    },
    "remove_definitions": {},
    "source_group": {
        "front_positional_arguments": ["<name>"],
        "one_value_keywords": ["REGULAR_EXPRESSION", "TREE", "PREFIX"],
        "multi_value_keywords": ["FILES"],
    },
    "set_source_files_properties": {
        "multi_value_keywords": ["PROPERTIES", "DIRECTORY", "TARGET_DIRECTORY"],
        "keyword_formatters": {"PROPERTIES": KeywordFormatter.Pairs},
    },
    "set_target_properties": {
        "multi_value_keywords": ["PROPERTIES"],
        "keyword_formatters": {"PROPERTIES": KeywordFormatter.Pairs},
    },
    "set_tests_properties": {
        "one_value_keywords": ["DIRECTORY"],
        "multi_value_keywords": ["PROPERTIES"],
        "keyword_formatters": {
            "PROPERTIES": KeywordFormatter.Pairs,
        },
    },
    "target_compile_definitions": {
        "front_positional_arguments": ["<target>"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_compile_features": {
        "front_positional_arguments": ["<target>"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_compile_options": {
        "front_positional_arguments": ["<target>"],
        "options": ["BEFORE"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_include_directories": {
        "front_positional_arguments": ["<target>"],
        "options": ["BEFORE", "SYSTEM", "AFTER"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_link_directories": {
        "front_positional_arguments": ["<target>"],
        "options": ["BEFORE"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_link_libraries": {
        "front_positional_arguments": ["<target>"],
        "multi_value_keywords": [
            "INTERFACE",
            "PUBLIC",
            "PRIVATE",
            "LINK_PRIVATE",
            "LINK_PUBLIC",
            "LINK_INTERFACE_LIBRARIES",
        ],
        "sections": {
            "INTERFACE": _debug_optimized_general,
            "PUBLIC": _debug_optimized_general,
            "PRIVATE": _debug_optimized_general,
            "LINK_PRIVATE": _debug_optimized_general,
            "LINK_PUBLIC": _debug_optimized_general,
            "LINK_INTERFACE_LIBRARIES": _debug_optimized_general,
        },
    },
    "target_link_options": {
        "front_positional_arguments": ["<target>"],
        "options": ["BEFORE"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_precompile_headers": {
        "front_positional_arguments": ["<target>"],
        "one_value_keywords": ["REUSE_FROM"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
    },
    "target_sources": {
        "_two_words_keywords": [_FILE_SET_Any],
        "front_positional_arguments": ["<target>"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
        "sections": {
            "INTERFACE": _target_sources_FILE_SET,
            "PUBLIC": _target_sources_FILE_SET,
            "PRIVATE": _target_sources_FILE_SET,
        },
    },
    "try_compile": {
        "front_positional_arguments": [
            "<compileResultVar>",
            "<bindir>",
            "<srcdir>",  # or "<srcfile>"
            "<projectName>",
            "<targetName>",
        ],
        "options": ["NO_CACHE", "NO_LOG"],
        "one_value_keywords": [
            "OUTPUT_VARIABLE",
            "COPY_FILE",
            "COPY_FILE_ERROR",
            "C_STANDARD",
            "C_STANDARD_REQUIRED",
            "C_EXTENSIONS",
            "CXX_STANDARD",
            "CXX_STANDARD_REQUIRED",
            "CXX_EXTENSIONS",
            "OBJC_STANDARD",
            "OBJC_STANDARD_REQUIRED",
            "OBJC_EXTENSIONS",
            "OBJCXX_STANDARD",
            "OBJCXX_STANDARD_REQUIRED",
            "OBJCXX_EXTENSIONS",
            "CUDA_STANDARD",
            "CUDA_STANDARD_REQUIRED",
            "CUDA_EXTENSIONS",
            "PROJECT",
            "SOURCE_DIR",
            "BINARY_DIR",
            "TARGET",
            "LOG_DESCRIPTION",
            "SOURCES_TYPE",
            "LINKER_LANGUAGE",
        ],
        "multi_value_keywords": [
            "SOURCES",
            "CMAKE_FLAGS",
            "COMPILE_DEFINITIONS",
            "LINK_OPTIONS",
            "LINK_LIBRARIES",
            "SOURCE_FROM_CONTENT",
            "SOURCE_FROM_VAR",
            "SOURCE_FROM_FILE",
        ],
    },
    "try_run": {
        "front_positional_arguments": [
            "<runResultVar>",
            "<compileResultVar>",
            "<bindir>",
            "<srcfile>",
        ],
        "options": ["NO_CACHE", "NO_LOG"],
        "one_value_keywords": [
            "COMPILE_OUTPUT_VARIABLE",
            "RUN_OUTPUT_VARIABLE",
            "OUTPUT_VARIABLE",
            "WORKING_DIRECTORY",
            "COPY_FILE",
            "COPY_FILE_ERROR",
            "C_STANDARD",
            "C_STANDARD_REQUIRED",
            "C_EXTENSIONS",
            "CXX_STANDARD",
            "CXX_STANDARD_REQUIRED",
            "CXX_EXTENSIONS",
            "OBJC_STANDARD",
            "OBJC_STANDARD_REQUIRED",
            "OBJC_EXTENSIONS",
            "OBJCXX_STANDARD",
            "OBJCXX_STANDARD_REQUIRED",
            "OBJCXX_EXTENSIONS",
            "CUDA_STANDARD",
            "CUDA_STANDARD_REQUIRED",
            "CUDA_EXTENSIONS",
            "RUN_OUTPUT_VARIABLE",
            "RUN_OUTPUT_STDOUT_VARIABLE",
            "RUN_OUTPUT_STDERR_VARIABLE",
            "LOG_DESCRIPTION",
        ],
        "multi_value_keywords": [
            "CMAKE_FLAGS",
            "COMPILE_DEFINITIONS",
            "LINK_OPTIONS",
            "LINK_LIBRARIES",
            "ARGS",
            "SOURCES",
            "SOURCE_FROM_CONTENT",
            "SOURCE_FROM_VAR",
            "SOURCE_FROM_FILE",
        ],
    },
    #
    ## CTest Commands
    #
    "ctest_build": {
        "options": ["APPEND", "QUIET"],
        "one_value_keywords": [
            "BUILD",
            "CONFIGURATION",
            "FLAGS",
            "PROJECT_NAME",
            "TARGET",
            "NUMBER_ERRORS",
            "NUMBER_WARNINGS",
            "RETURN_VALUE",
            "CAPTURE_CMAKE_ERROR",
            "PARALLEL_LEVEL",
        ],
    },
    "ctest_configure": {
        "options": ["APPEND", "QUIET"],
        "one_value_keywords": [
            "BUILD",
            "SOURCE",
            "OPTIONS",
            "RETURN_VALUE",
            "CAPTURE_CMAKE_ERROR",
        ],
    },
    "ctest_coverage": {
        "options": ["APPEND", "QUIET"],
        "one_value_keywords": ["BUILD", "RETURN_VALUE", "CAPTURE_CMAKE_ERROR"],
        "multi_value_keywords": ["LABELS"],
    },
    "ctest_empty_binary_directory": {},
    "ctest_memcheck": {
        "options": ["APPEND", "QUIET"],
        "one_value_keywords": [
            "BUILD",
            "START",
            "END",
            "STRIDE",
            "EXCLUDE",
            "INCLUDE",
            "EXCLUDE_LABEL",
            "INCLUDE_LABEL",
            "EXCLUDE_FIXTURE",
            "EXCLUDE_FIXTURE_SETUP",
            "EXCLUDE_FIXTURE_CLEANUP",
            "PARALLEL_LEVEL",
            "TEST_LOAD",
            "SCHEDULE_RANDOM",
            "STOP_TIME",
            "RETURN_VALUE",
            "DEFECT_COUNT",
        ],
    },
    "ctest_read_custom_files": {},
    "ctest_run_script": {
        "one_value_keywords": ["RETURN_VALUE"],
    },
    "ctest_sleep": {},
    "ctest_start": {
        "front_positional_arguments": ["<model>", "<source>", "<binary>"],
        "options": ["APPEND", "QUIET"],
        "one_value_keywords": ["GROUP"],
    },
    "ctest_submit": {
        "options": ["QUIET"],
        "one_value_keywords": [
            "SUBMIT_URL",
            "BUILD_ID",
            "HTTPHEADER",
            "RETRY_COUNT",
            "RETRY_DELAY",
            "RETURN_VALUE",
            "CAPTURE_CMAKE_ERROR",
            "CDASH_UPLOAD",
            "CDASH_UPLOAD_TYPE",
        ],
        "multi_value_keywords": ["PARTS", "FILES"],
    },
    "ctest_test": {
        "options": ["APPEND", "QUIET"],
        "one_value_keywords": [
            "BUILD",
            "START",
            "END",
            "STRIDE",
            "EXCLUDE",
            "INCLUDE",
            "EXCLUDE_LABEL",
            "INCLUDE_LABEL",
            "EXCLUDE_FIXTURE",
            "EXCLUDE_FIXTURE_SETUP",
            "EXCLUDE_FIXTURE_CLEANUP",
            "PARALLEL_LEVEL",
            "RESOURCE_SPEC_FILE",
            "TEST_LOAD",
            "SCHEDULE_RANDOM",
            "STOP_TIME",
            "RETURN_VALUE",
            "CAPTURE_CMAKE_ERROR",
            "INCLUDE_FROM_FILE",
            "EXCLUDE_FROM_FILE",
        ],
    },
    "ctest_update": {
        "options": ["QUIET"],
        "one_value_keywords": ["SOURCE", "RETURN_VALUE", "CAPTURE_CMAKE_ERROR"],
    },
    "ctest_upload": {
        "options": ["QUIET"],
        "one_value_keywords": ["CAPTURE_CMAKE_ERROR"],
        "multi_value_keywords": ["FILES"],
    },
    #
    ## Deprecated Commands
    #
    "build_name": {},
    "exec_program": {},
    "export_library_dependencies": {},
    "install_files": {},
    "install_programs": {},
    "install_targets": {},
    "load_command": {},
    "make_directory": {},
    "output_required_files": {},
    "qt_wrap_cpp": {},
    "qt_wrap_ui": {},
    "remove": {},
    "subdir_depends": {},
    "subdirs": {},
    "use_mangled_mesa": {},
    "utility_source": {},
    "variable_requires": {},
    "write_file": {},
    # cmake-modules
    #
    ## Utility Modules
    #
    ### AddFileDependencies
    "add_file_dependencies": {},
    #
    ### AndroidTestUtilities
    "android_add_test_data": {
        "one_value_keywords": [
            "FILES_DEST",
            "LIBS_DEST",
            "DEVICE_OBJECT_STORE",
            "DEVICE_TEST_DIR",
        ],
        "multi_value_keywords": ["FILES", "LIBS", "NO_LINK_REGEX"],
    },
    #
    ### BundleUtilities
    "fixup_bundle": {},
    "copy_and_fixup_bundle": {},
    "verify_app": {},
    "get_bundle_main_executable": {},
    "get_dotapp_dir": {},
    "get_bundle_and_executable": {},
    "get_bundle_all_executables": {},
    "get_item_key": {},
    "get_item_rpaths": {},
    "clear_bundle_keys": {},
    "set_bundle_key_values": {},
    "get_bundle_keys": {},
    "copy_resolved_item_into_bundle": {},
    "copy_resolved_framework_into_bundle": {},
    "fixup_bundle_item": {},
    "verify_bundle_prerequisites": {},
    "verify_bundle_symlinks": {},
    #
    ### CheckCompilerFlag
    "check_compiler_flag": {},
    #
    ### CheckCCompilerFlag
    "check_c_compiler_flag": {},
    #
    ### CheckCSourceCompiles
    "check_c_source_compiles": {
        "multi_value_keywords": ["FAIL_REGEX"],
    },
    #
    ### CheckCSourceRuns
    "check_c_source_runs": {},
    #
    ### CheckCXXCompilerFlag
    "check_cxx_compiler_flag": {},
    #
    ### CheckCXXSourceCompiles
    "check_cxx_source_compiles": {
        "multi_value_keywords": ["FAIL_REGEX"],
    },
    #
    ### CheckCXXSourceRuns
    "check_cxx_source_runs": {},
    #
    ### CheckCXXSymbolExists
    "check_cxx_symbol_exists": {},
    #
    ### CheckFortranCompilerFlag
    "check_fortran_compiler_flag": {},
    #
    ### CheckFortranFunctionExists
    # (&)
    "check_fortran_function_exists": {},
    #
    ### CheckFortranSourceCompiles
    "check_fortran_source_compiles": {
        "one_value_keywords": ["SRC_EXT"],
        "multi_value_keywords": ["FAIL_REGEX"],
    },
    #
    ### CheckFortranSourceRuns
    "check_fortran_source_runs": {
        "one_value_keywords": ["SRC_EXT"],
    },
    #
    ### CheckFunctionExists
    "check_function_exists": {},
    #
    ### CheckIPOSupported
    "check_ipo_supported": {
        "one_value_keywords": ["RESULT", "OUTPUT"],
        "multi_value_keywords": ["LANGUAGES"],
    },
    #
    ### CheckIncludeFileCXX
    # (&)
    "check_include_file_cxx": {},
    #
    ### CheckIncludeFile
    # (&)
    "check_include_file": {},
    #
    ### CheckIncludeFiles
    # (&)
    "check_include_files": {
        "one_value_keywords": ["LANGUAGE"],
    },
    #
    ### CheckLanguage
    "check_language": {},
    #
    ### CheckLibraryExists
    # (&)
    "check_library_exists": {},
    #
    ### CheckLinkerFlag
    "check_linker_flag": {},
    #
    ### CheckOBJCCompilerFlag
    "check_objc_compiler_flag": {},
    #
    ### CheckOBJCSourceCompiles
    "check_objc_source_compiles": {
        "multi_value_keywords": ["FAIL_REGEX"],
    },
    #
    ### CheckOBJCSourceRuns
    "check_objc_source_runs": {},
    #
    ### CheckOBJCXXCompilerFlag
    "check_objcxx_compiler_flag": {},
    #
    ### CheckOBJCXXSourceCompiles
    "check_objcxx_source_compiles": {
        "multi_value_keywords": ["FAIL_REGEX"],
    },
    #
    ### CheckOBJCXXSourceRuns
    "check_objcxx_source_runs": {},
    #
    ### CheckPIESupported
    "check_pie_supported": {
        "one_value_keywords": ["OUTPUT_VARIABLE"],
        "multi_value_keywords": ["LANGUAGES"],
    },
    #
    ### CheckPrototypeDefinition
    "check_prototype_definition": {},
    #
    ### CheckSourceCompiles
    "check_source_compiles": {
        "front_positional_arguments": ["<lang>", "<code>", "<resultVar>"],
        "one_value_keywords": ["SRC_EXT"],
        "multi_value_keywords": ["FAIL_REGEX"],
    },
    #
    ### CheckSourceRuns
    "check_source_runs": {
        "front_positional_arguments": ["<lang>", "<code>", "<resultVar>"],
        "one_value_keywords": ["SRC_EXT"],
    },
    #
    ### CheckStructHasMember
    # (&)
    "check_struct_has_member": {
        "one_value_keywords": ["LANGUAGE"],
    },
    #
    ### CheckSymbolExists
    "check_symbol_exists": {},
    #
    ### CheckTypeSize
    "check_type_size": {
        "options": ["BUILTIN_TYPES_ONLY"],
        "one_value_keywords": ["LANGUAGE"],
    },
    #
    ### CheckVariableExists
    # (&)
    "check_variable_exists": {},
    #
    ### CMakeAddFortranSubdirectory
    "cmake_add_fortran_subdirectory": {
        "options": ["NO_EXTERNAL_INSTALL", "LINK_LIBRARIES"],
        "one_value_keywords": ["PROJECT", "ARCHIVE_DIR", "RUNTIME_DIR"],
        "multi_value_keywords": ["LIBRARIES", "LINK_LIBS", "CMAKE_COMMAND_LINE"],
        "keyword_formatters": {"CMAKE_COMMAND_LINE": KeywordFormatter.CommandLine},
    },
    #
    ### CMakeBackwardCompatibilityCXX
    #### no commands
    #
    ### CMakeDependentOption
    "cmake_dependent_option": {},
    #
    ### CMakeFindDependencyMacro
    "find_dependency": {},
    #
    ### CMakeFindFrameworks
    "cmake_find_frameworks": {},
    #
    ### CMakeFindPackageMode
    #### no commands
    #
    ### CMakeGraphVizOptions
    #### no commands
    #
    ### CMakePackageConfigHelpers
    "configure_package_config_file": {
        "front_positional_arguments": ["<input>", "<output>"],
        "options": ["NO_SET_AND_CHECK_MACRO", "NO_CHECK_REQUIRED_COMPONENTS_MACRO"],
        "one_value_keywords": ["INSTALL_DESTINATION", "INSTALL_PREFIX"],
        "multi_value_keywords": ["PATH_VARS"],
    },
    "generate_apple_architecture_selection_file": {
        "front_positional_arguments": ["<filename>"],
        "one_value_keywords": [
            "INSTALL_DESTINATION",
            "INSTALL_PREFIX",
            "UNIVERSAL_INCLUDE_FILE",
            "ERROR_VARIABLE",
        ],
        "multi_value_keywords": [
            "SINGLE_ARCHITECTURES",
            "SINGLE_ARCHITECTURE_INCLUDE_FILES",
            "UNIVERSAL_ARCHITECTURES",
        ],
    },
    "generate_apple_platform_selection_file": {
        "front_positional_arguments": ["<filename>"],
        "one_value_keywords": [
            "INSTALL_DESTINATION",
            "INSTALL_PREFIX",
            "MACOS_INCLUDE_FILE",
            "IOS_INCLUDE_FILE",
            "IOS_SIMULATOR_INCLUDE_FILE",
            "IOS_CATALYST_INCLUDE_FILE",
            "TVOS_INCLUDE_FILE",
            "TVOS_SIMULATOR_INCLUDE_FILE",
            "WATCHOS_INCLUDE_FILE",
            "WATCHOS_SIMULATOR_INCLUDE_FILE",
            "VISIONOS_INCLUDE_FILE",
            "VISIONOS_SIMULATOR_INCLUDE_FILE",
            "ERROR_VARIABLE",
        ],
    },
    "write_basic_package_version_file": {
        "options": ["ARCH_INDEPENDENT"],
        "one_value_keywords": ["VERSION", "COMPATIBILITY"],
    },
    #
    ### CMakePrintHelpers
    "cmake_print_properties": {
        "multi_value_keywords": [
            "TARGETS",
            "SOURCES",
            "DIRECTORIES",
            "TESTS",
            "CACHE_ENTRIES",
            "PROPERTIES",
        ]
    },
    "cmake_print_variables": {},
    #
    ### CMakePrintSystemInformation
    #### no commands
    #
    ### CMakePushCheckState
    "cmake_push_check_state": {},
    "cmake_pop_check_state": {},
    "cmake_reset_check_state": {},
    #
    ### CMakeVerifyManifest
    #### no commands
    #
    ### CPackComponent
    "cpack_add_component": {
        "options": ["HIDDEN", "REQUIRED", "DISABLED", "DOWNLOADED"],
        "one_value_keywords": [
            "DISPLAY_NAME",
            "DESCRIPTION",
            "GROUP",
            "ARCHIVE_FILE",
            "PLIST",
        ],
        "multi_value_keywords": ["DEPENDS", "INSTALL_TYPES"],
    },
    "cpack_add_component_group": {
        "options": ["EXPANDED", "BOLD_TITLE"],
        "one_value_keywords": ["DISPLAY_NAME", "DESCRIPTION", "PARENT_GROUP"],
    },
    "cpack_add_install_type": {
        "one_value_keywords": ["DISPLAY_NAME"],
    },
    "cpack_configure_downloads": {
        "options": ["ALL", "ADD_REMOVE", "NO_ADD_REMOVE"],
        "one_value_keywords": ["UPLOAD_DIRECTORY"],
    },
    #
    ### CPackIFW
    "cpack_ifw_add_package_resources": {},
    "cpack_ifw_add_repository": {
        "options": ["DISABLED"],
        "one_value_keywords": ["URL", "USERNAME", "PASSWORD", "DISPLAY_NAME"],
    },
    "cpack_ifw_configure_component": {
        "options": [
            "COMMON",
            "ESSENTIAL",
            "VIRTUAL",
            "FORCED_INSTALLATION",
            "REQUIRES_ADMIN_RIGHTS",
        ],
        "one_value_keywords": [
            "NAME",
            "DISPLAY_NAME",
            "DESCRIPTION",
            "UPDATE_TEXT",
            "VERSION",
            "RELEASE_DATE",
            "SCRIPT",
            "PRIORITY",
            "SORTING_PRIORITY",
            "CHECKABLE",
            "DEFAULT",
        ],
        "multi_value_keywords": [
            "DEPENDS",
            "DEPENDENCIES",
            "AUTO_DEPEND_ON",
            "LICENSES",
            "USER_INTERFACES",
            "TRANSLATIONS",
            "REPLACES",
        ],
    },
    "cpack_ifw_configure_component_group": {
        "options": [
            "VIRTUAL",
            "FORCED_INSTALLATION",
            "REQUIRES_ADMIN_RIGHTS",
        ],
        "one_value_keywords": [
            "NAME",
            "DISPLAY_NAME",
            "DESCRIPTION",
            "UPDATE_TEXT",
            "VERSION",
            "RELEASE_DATE",
            "SCRIPT",
            "PRIORITY",
            "SORTING_PRIORITY",
            "DEFAULT",
            "CHECKABLE",
        ],
        "multi_value_keywords": [
            "DEPENDS",
            "DEPENDENCIES",
            "AUTO_DEPEND_ON",
            "LICENSES",
            "USER_INTERFACES",
            "TRANSLATIONS",
            "REPLACES",
        ],
    },
    "cpack_ifw_update_repository": {
        "options": ["ADD", "REMOVE", "REPLACE", "DISABLED"],
        "one_value_keywords": [
            "URL",
            "OLD_URL",
            "NEW_URL",
            "USERNAME",
            "PASSWORD",
            "DISPLAY_NAME",
        ],
    },
    #
    ### CPackIFWConfigureFile
    "cpack_ifw_configure_file": {},
    #
    ### CPack
    #### no commands
    #
    ### CSharpUtilities
    "csharp_get_dependentupon_name": {},
    "csharp_get_filename_key_base": {},
    "csharp_get_filename_keys": {},
    "csharp_set_designer_cs_properties": {},
    "csharp_set_windows_forms_properties": {},
    "csharp_set_xaml_cs_properties": {},
    #
    ### CTest
    #### no commands
    #
    ### CTestCoverageCollectGCOV
    "ctest_coverage_collect_gcov": {
        "options": ["GLOB", "DELETE", "QUIET"],
        "one_value_keywords": ["TARBALL", "SOURCE", "BUILD", "GCOV_COMMAND"],
        "multi_value_keywords": ["GCOV_OPTIONS"],
        "keyword_formatters": {"GCOV_OPTIONS": KeywordFormatter.CommandLine},
    },
    #
    ### CTestScriptMode
    #
    ### CTestUseLaunchers
    #
    ### Dart
    #
    ### DeployQt4
    "write_qt4_conf": {},
    "resolve_qt4_paths": {},
    "fixup_qt4_executable": {},
    "install_qt4_executable": {},
    "install_qt4_plugin": {},
    "install_qt4_plugin_path": {},
    #
    ### Documentation
    #
    ### ExternalData
    "ExternalData_Expand_Arguments": {},
    "ExternalData_Add_Test": {},
    "ExternalData_Add_Target": {
        "front_positional_arguments": ["<target>"],
        "one_value_keywords": ["SHOW_PROGRESS"],
    },
    #
    ### ExternalProject
    "ExternalProject_Add": {
        "one_value_keywords": [
            # Directory
            "PREFIX",
            "TMP_DIR",
            "STAMP_DIR",
            "LOG_DIR",
            "DOWNLOAD_DIR",
            "SOURCE_DIR",
            "BINARY_DIR",
            "INSTALL_DIR",
            # Download Step
            *_ExternalProject_Add_DownloadStep["one_value_keywords"],
            # Update Step
            *_ExternalProject_Add_UpdateStep["one_value_keywords"],
            # Patch Step
            *_ExternalProject_Add_PatchStep["one_value_keywords"],
            # Configure Step
            "CMAKE_COMMAND",
            "CMAKE_GENERATOR",
            "CMAKE_GENERATOR_PLATFORM",
            "CMAKE_GENERATOR_TOOLSET",
            "CMAKE_GENERATOR_INSTANCE",
            "SOURCE_SUBDIR",
            "CONFIGURE_HANDLED_BY_BUILD",
            # Build Step
            "BUILD_IN_SOURCE",
            "BUILD_ALWAYS",
            "BUILD_JOB_SERVER_AWARE",
            # Install Step
            "INSTALL_JOB_SERVER_AWARE",
            # Test Step
            "TEST_BEFORE_INSTALL",
            "TEST_AFTER_INSTALL",
            "TEST_EXCLUDE_FROM_MAIN",
            # Output Logging
            "LOG_DOWNLOAD",
            "LOG_UPDATE",
            "LOG_PATCH",
            "LOG_CONFIGURE",
            "LOG_BUILD",
            "LOG_INSTALL",
            "LOG_TEST",
            "LOG_MERGED_STDOUTERR",
            "LOG_OUTPUT_ON_FAILURE",
            # Terminal Access
            "USES_TERMINAL_DOWNLOAD",
            "USES_TERMINAL_UPDATE",
            "USES_TERMINAL_PATCH",
            "USES_TERMINAL_CONFIGURE",
            "USES_TERMINAL_BUILD",
            "USES_TERMINAL_INSTALL",
            "USES_TERMINAL_TEST",
            # Target
            "EXCLUDE_FROM_ALL",
            # Miscellaneous
            "LIST_SEPARATOR",
        ],
        "multi_value_keywords": [
            # Download Step
            *_ExternalProject_Add_DownloadStep["multi_value_keywords"],
            # Update Step
            *_ExternalProject_Add_UpdateStep["multi_value_keywords"],
            # Patch Step
            *_ExternalProject_Add_PatchStep["multi_value_keywords"],
            # Configure Step
            "CONFIGURE_COMMAND",
            "CMAKE_ARGS",
            "CMAKE_CACHE_ARGS",
            "CMAKE_CACHE_DEFAULT_ARGS",
            # Build Step
            "BUILD_COMMAND",
            "BUILD_BYPRODUCTS",
            # Install Step
            "INSTALL_COMMAND",
            "INSTALL_BYPRODUCTS",
            # Test Step
            "TEST_COMMAND",
            # Output Logging
            # Terminal Access
            # Target
            "DEPENDS",
            "STEP_TARGETS",
            "INDEPENDENT_STEP_TARGETS",
            # Miscellaneous
            "COMMAND",
        ],
        "keyword_formatters": {
            key: KeywordFormatter.CommandLine
            for key in [
                "DOWNLOAD_COMMAND",
                "GIT_CONFIG",
                "UPDATE_COMMAND",
                "PATCH_COMMAND",
                "CONFIGURE_COMMAND",
                "CMAKE_ARGS",
                "CMAKE_CACHE_ARGS",
                "CMAKE_CACHE_DEFAULT_ARGS",
                "BUILD_COMMAND",
                "INSTALL_COMMAND",
                "TEST_COMMAND",
                "COMMAND",
            ]
        },
    },
    "ExternalProject_Add_Step": {
        "one_value_keywords": [
            "COMMENT",
            "ALWAYS",
            "EXCLUDE_FROM_MAIN",
            "WORKING_DIRECTORY",
            "LOG",
            "USES_TERMINAL",
        ],
        "multi_value_keywords": [
            "COMMAND",
            "DEPENDEES",
            "DEPENDERS",
            "DEPENDS",
            "BYPRODUCTS",
        ],
        "keyword_formatters": {"COMMAND": KeywordFormatter.CommandLine},
    },
    "ExternalProject_Add_StepDependencies": {},
    "ExternalProject_Add_StepTargets": {},
    "ExternalProject_Get_Property": {},
    #
    ### FeatureSummary
    "add_feature_info": {},
    "feature_summary": {
        "options": [
            "APPEND",
            "INCLUDE_QUIET_PACKAGES",
            "FATAL_ON_MISSING_REQUIRED_PACKAGES",
            "QUIET_ON_EMPTY",
            "DEFAULT_DESCRIPTION",
        ],
        "one_value_keywords": ["FILENAME", "VAR", "DESCRIPTION", "WHAT"],
    },
    "print_disabled_features": {},
    "print_enabled_features": {},
    "set_feature_info": {},
    "set_package_info": {},
    "set_package_properties": {
        "multi_value_keywords": ["PROPERTIES"],
        "keyword_formatters": {"PROPERTIES": KeywordFormatter.Pairs},
    },
    #
    ### FetchContent
    "FetchContent_Declare": {
        "options": ["SYSTEM", "OVERRIDE_FIND_PACKAGE", "EXCLUDE_FROM_ALL"],
        "one_value_keywords": [
            # Download Step
            *_ExternalProject_Add_DownloadStep["one_value_keywords"],
            # Update Step
            *_ExternalProject_Add_UpdateStep["one_value_keywords"],
            # Patch Step
            *_ExternalProject_Add_PatchStep["one_value_keywords"],
        ],
        "multi_value_keywords": [
            "FIND_PACKAGE_ARGS",
            # Download Step
            *_ExternalProject_Add_DownloadStep["multi_value_keywords"],
            # Update Step
            *_ExternalProject_Add_UpdateStep["multi_value_keywords"],
            # Patch Step
            *_ExternalProject_Add_PatchStep["multi_value_keywords"],
        ],
        "keyword_formatters": {
            key: KeywordFormatter.CommandLine
            for key in ["DOWNLOAD_COMMAND", "UPDATE_COMMAND", "PATCH_COMMAND"]
        },
    },
    "FetchContent_GetProperties": {
        "one_value_keywords": ["SOURCE_DIR", "BINARY_DIR", "POPULATED"],
    },
    "FetchContent_MakeAvailable": {},
    "FetchContent_Populate": {
        "options": ["QUIET"],
        "one_value_keywords": [
            "SUBBUILD_DIR",
            "SOURCE_DIR",
            "BINARY_DIR",
            # Same as externalproject_add
            # Download Step
            "URL_HASH",
            "URL_MD5",
            "DOWNLOAD_NAME",
            "DOWNLOAD_NO_EXTRACT",
            "TIMEOUT",
            "HTTP_USERNAME",
            "HTTP_PASSWORD",
            "TLS_VERIFY",
            "TLS_CAINFO",
            "NETRC",
            "NETRC_FILE",
            "GIT_REPOSITORY",
            "GIT_TAG",
            "GIT_REMOTE_NAME",
            "GIT_SUBMODULES_RECURSE",
            "GIT_SHALLOW",
            "GIT_PROGRESS",
            "GIT_REMOTE_UPDATE_STRATEGY",
            "SVN_REPOSITORY",
            "SVN_REVISION",
            "SVN_USERNAME",
            "SVN_PASSWORD",
            "SVN_TRUST_CERT",
            "HG_REPOSITORY",
            "HG_TAG",
            "CVS_REPOSITORY",
            "CVS_MODULE",
            "CVS_TAG",
            # Update/Patch Step
            "UPDATE_DISCONNECTED",
        ],
        "multi_value_keywords": [
            # Same as externalproject_add
            # Download Step
            "DOWNLOAD_COMMAND",
            "URL",
            "HTTP_HEADER",
            "GIT_SUBMODULES",
            "GIT_CONFIG",
            # Update/Patch Step
            "UPDATE_COMMAND",
            "PATCH_COMMAND",
        ],
    },
    "FetchContent_SetPopulated": {
        "front_positional_arguments": ["<name>"],
        "one_value_keywords": ["SOURCE_DIR", "BINARY_DIR"],
    },
    #
    ### FindPackageHandleStandardArgs
    "find_package_check_version": {
        "options": ["HANDLE_VERSION_RANGE"],
        "one_value_keywords": ["RESULT_MESSAGE_VARIABLE"],
    },
    "find_package_handle_standard_args": {
        "options": ["HANDLE_COMPONENTS", "CONFIG_MODE", "NAME_MISMATCHED"],
        "one_value_keywords": [
            "FOUND_VAR",
            "VERSION_VAR",
            "REASON_FAILURE_MESSAGE",
            "FAIL_MESSAGE",
        ],
        "multi_value_keywords": ["REQUIRED_VARS"],
    },
    #
    ### FindPackageMessage
    "find_package_message": {},
    #
    ### FortranCInterface
    "FortranCInterface_HEADER": {
        "one_value_keywords": ["MACRO_NAMESPACE", "SYMBOL_NAMESPACE"],
        "multi_value_keywords": ["SYMBOLS"],
    },
    "FortranCInterface_VERIFY": {},
    #
    ### GenerateExportHeader
    "generate_export_header": {
        "options": ["DEFINE_NO_DEPRECATED"],
        "one_value_keywords": [
            "BASE_NAME",
            "EXPORT_MACRO_NAME",
            "EXPORT_FILE_NAME",
            "DEPRECATED_MACRO_NAME",
            "NO_EXPORT_MACRO_NAME",
            "INCLUDE_GUARD_NAME",
            "STATIC_DEFINE",
            "NO_DEPRECATED_MACRO_NAME",
            "PREFIX_NAME",
            "CUSTOM_CONTENT_FROM_VARIABLE",
        ],
    },
    "add_compiler_export_flags": {},
    #
    ### GetPrerequisites
    "get_prerequisites": {},
    "list_prerequisites": {},
    "list_prerequisites_by_glob": {},
    "gp_append_unique": {},
    "is_file_executable": {},
    "gp_item_default_embedded_path": {},
    "gp_file_type": {},
    "gp_resolved_file_type": {},
    "gp_resolve_item": {},
    #
    ### GNUInstallDirs
    "GNUInstallDirs_get_absolute_install_dir": {},
    #
    ### GoogleTest
    "gtest_add_tests": {
        "options": ["SKIP_DEPENDENCY"],
        "one_value_keywords": [
            "TARGET",
            "WORKING_DIRECTORY",
            "TEST_PREFIX",
            "TEST_SUFFIX",
            "TEST_LIST",
        ],
        "multi_value_keywords": ["SOURCES", "EXTRA_ARGS"],
    },
    "gtest_discover_tests": {
        "front_positional_arguments": ["<target>"],
        "options": ["NO_PRETTY_TYPES", "NO_PRETTY_VALUES"],
        "one_value_keywords": [
            "WORKING_DIRECTORY",
            "TEST_PREFIX",
            "TEST_SUFFIX",
            "TEST_FILTER",
            "TEST_LIST",
            "DISCOVERY_TIMEOUT",
            "XML_OUTPUT_DIR",
            "DISCOVERY_MODE",
        ],
        "multi_value_keywords": ["EXTRA_ARGS", "PROPERTIES", "DISCOVERY_EXTRA_ARGS"],
        "keyword_formatters": {
            "EXTRA_ARGS": KeywordFormatter.CommandLine,
            "PROPERTIES": KeywordFormatter.Pairs,
            "DISCOVERY_EXTRA_ARGS": KeywordFormatter.CommandLine,
        },
    },
    #
    ### InstallRequiredSystemLibraries
    #
    ### ProcessorCount
    "ProcessorCount": {},
    #
    ### SelectLibraryConfigurations
    "select_library_configurations": {},
    #
    ### SquishTestScript
    #
    ### TestBigEndian
    "test_big_endian": {},
    #
    ### TestForANSIForScope
    #
    ### TestForANSIStreamHeaders
    #
    ### TestForSSTREAM
    #
    ### TestForSTDNamespace
    #
    ### UseEcos
    "ecos_add_executable": {},
    "ecos_add_include_directories": {},
    "ecos_adjust_directory": {},
    "ecos_use_arm_elf_tools": {},
    "ecos_use_i386_elf_tools": {},
    "ecos_use_ppc_eabi_tools": {},
    #
    ### UseJavaClassFilelist
    #
    ### UseJava
    "add_jar": {
        "options": ["RESOURCES"],
        "one_value_keywords": [
            "ENTRY_POINT",
            "VERSION",
            "OUTPUT_NAME",
            "OUTPUT_DIR",
            "GENERATE_NATIVE_HEADERS",
            "DESTINATION",
            "BUILD",
        ],
        "multi_value_keywords": ["SOURCES", "INCLUDE_JARS", "NAMESPACE"],
    },
    "install_jar": {
        "one_value_keywords": ["DESTINATION", "COMPONENT"],
    },
    "install_jni_symlink": {
        "one_value_keywords": ["DESTINATION", "COMPONENT"],
    },
    "install_jar_exports": {
        "one_value_keywords": ["NAMESPACE", "FILE", "DESTINATION", "COMPONENT"],
        "multi_value_keywords": ["TARGETS"],
    },
    "export_jars": {
        "one_value_keywords": ["NAMESPACE", "FILE"],
        "multi_value_keywords": ["TARGETS"],
    },
    "find_jar": {
        "one_value_keywords": ["DOC", "ENV"],
        "multi_value_keywords": ["NAMES", "PATHS", "VERSIONS"],
    },
    "create_javadoc": {
        "one_value_keywords": [
            "SOURCEPATH",
            "CLASSPATH",
            "INSTALLPATH",
            "DOCTITLE",
            "WINDOWTITLE",
            "AUTHOR",
            "USE",
            "VERSION",
        ],
        "multi_value_keywords": ["PACKAGES", "FILES"],
    },
    "create_javah": {
        "one_value_keywords": [
            "TARGET",
            "GENERATED_FILES",
            "OUTPUT_NAME",
            "OUTPUT_DIR",
        ],
        "multi_value_keywords": ["CLASSES", "CLASSPATH", "DEPENDS"],
    },
    #
    ### UseJavaSymlinks
    #
    ### UseSWIG
    "swig_add_library": {
        "options": ["NO_PROXY"],
        "one_value_keywords": ["TYPE", "LANGUAGE", "OUTPUT_DIR", "OUTFILE_DIR"],
        "multi_value_keywords": ["SOURCES"],
    },
    "swig_link_libraries": {},
    #
    ### UsewxWidgets
    #
    ### WriteCompilerDetectionHeader
    "write_compiler_detection_header": {
        "options": ["ALLOW_UNKNOWN_COMPILERS", "ALLOW_UNKNOWN_COMPILER_VERSIONS"],
        "one_value_keywords": [
            "FILE",
            "PREFIX",
            "OUTPUT_FILES_VAR",
            "OUTPUT_DIR",
            "VERSION",
            "PROLOG",
            "EPILOG",
        ],
        "multi_value_keywords": ["COMPILERS", "FEATURES", "BARE_FEATURES"],
    },
    #
    ## Find Modules
    #
    ### FindALSA
    #
    ### FindArmadillo
    #
    ### FindASPELL
    #
    ### FindAVIFile
    #
    ### FindBISON
    "bison_target": {
        "one_value_keywords": [
            "COMPILE_FLAGS",
            "DEFINES_FILE",
            "VERBOSE",
            "REPORT_FILE",
        ],
        "multi_value_keywords": ["OPTIONS"],
    },
    #
    ### FindBLAS
    #
    ### FindBacktrace
    #
    ### FindBoost
    #
    ### FindBullet
    #
    ### FindBZip2
    #
    ### FindCABLE
    #
    ### FindCoin3D
    #
    ### FindCups
    #
    ### FindCUDAToolkit
    #
    ### FindCURL
    #
    ### FindCurses
    #
    ### FindCVS
    #
    ### FindCxxTest
    "cxxtest_add_test": {},
    #
    ### FindCygwin
    #
    ### FindDart
    #
    ### FindDCMTK
    #
    ### FindDevIL
    #
    ### FindDoxygen
    "doxygen_add_docs": {
        "front_positional_arguments": ["targetName"],
        "options": ["ALL", "USE_STAMP_FILE"],
        "one_value_keywords": ["WORKING_DIRECTORY", "COMMENT", "CONFIG_FILE"],
    },
    #
    ### FindEnvModules
    "env_module": {
        "one_value_keywords": ["OUTPUT_VARIABLE", "RESULT_VARIABLE"],
        "multi_value_keywords": ["COMMAND"],
        "keyword_formatters": {"COMMAND": KeywordFormatter.CommandLine},
    },
    "env_module_swap": {
        "one_value_keywords": ["OUTPUT_VARIABLE", "RESULT_VARIABLE"],
    },
    "env_module_list": {},
    "env_module_avail": {},
    #
    ### FindEXPAT
    #
    ### FindFLEX
    "flex_target": {
        "one_value_keywords": ["COMPILE_FLAGS", "DEFINES_FILE"],
        "multi_value_keywords": ["OPTIONS"],
    },
    "add_flex_bison_dependency": {},
    #
    ### FindFLTK2
    #
    ### FindFLTK
    #
    ### FindFontconfig
    #
    ### FindFreetype
    #
    ### FindGCCXML
    #
    ### FindGDAL
    #
    ### FindGettext
    "gettext_create_translations": {
        "options": ["ALL"],
    },
    "gettext_process_pot_file": {
        "options": ["ALL"],
        "one_value_keywords": ["INSTALL_DESTINATION"],
        "multi_value_keywords": ["LANGUAGES"],
    },
    "gettext_process_po_files": {
        "options": ["ALL"],
        "one_value_keywords": ["INSTALL_DESTINATION"],
        "multi_value_keywords": ["PO_FILES"],
    },
    #
    ### FindGIF
    #
    ### FindGit
    #
    ### FindGLEW
    #
    ### FindGLUT
    #
    ### FindGnuplot
    #
    ### FindGnuTLS
    #
    ### FindGSL
    #
    ### FindGTest
    #
    ### FindGTK2
    #
    ### FindGTK
    #
    ### FindHDF5
    #
    ### FindHg
    # (&)
    "hg_wc_info": {},
    #
    ### FindHSPELL
    #
    ### FindHTMLHelp
    #
    ### FindIce
    #
    ### FindIcotool
    #
    ### FindICU
    #
    ### FindImageMagick
    #
    ### FindIconv
    #
    ### FindIntl
    #
    ### FindITK
    #
    ### FindJasper
    #
    ### FindJava
    #
    ### FindJNI
    #
    ### FindJPEG
    #
    ### FindKDE3
    "kde3_automoc": {},
    "kde3_add_moc_files": {},
    "kde3_add_dcop_skels": {},
    "kde3_add_dcop_stubs": {},
    "kde3_add_ui_files": {},
    "kde3_add_kcfg_files": {},
    "kde3_install_libtool_file": {},
    "kde3_add_executable": {},
    "kde3_add_kpart": {},
    "kde3_add_kdeinit_executable": {},
    #
    ### FindKDE4
    #
    ### FindLAPACK
    #
    ### FindLATEX
    #
    ### FindLibArchive
    #
    ### FindLibinput
    #
    ### FindLibLZMA
    #
    ### FindLibXml2
    #
    ### FindLibXslt
    #
    ### FindLTTngUST
    #
    ### FindLua50
    #
    ### FindLua51
    #
    ### FindLua
    #
    ### FindMatlab
    "matlab_get_version_from_release_name": {},
    "matlab_get_release_name_from_version": {},
    "matlab_add_unit_test": {
        "options": ["NO_UNITTEST_FRAMEWORK"],
        "one_value_keywords": [
            "NAME",
            "UNITTEST_FILE",
            "CUSTOM_TEST_COMMAND",
            "UNITTEST_PRECOMMAND",
            "TIMEOUT",
        ],
        "multi_value_keywords": [
            "ADDITIONAL_PATH",
            "MATLAB_ADDITIONAL_STARTUP_OPTIONS",
            "TEST_ARGS",
        ],
        "keyword_formatters": {
            "MATLAB_ADDITIONAL_STARTUP_OPTIONS": KeywordFormatter.CommandLine
        },
    },
    "matlab_add_mex": {
        "options": [
            "EXECUTABLE",
            "MODULE",
            "SHARED",
            "R2017b",
            "R2018a",
            "EXCLUDE_FROM_ALL",
            "NO_IMPLICIT_LINK_TO_MATLAB_LIBRARIES",
        ],
        "one_value_keywords": ["NAME", "OUTPUT_NAME", "DOCUMENTATION"],
        "multi_value_keywords": ["SRC", "LINK_TO"],
    },
    "matlab_extract_all_installed_versions_from_registry": {
        "one_value_keywords": ["REGISTRY_VIEW"],
    },
    "matlab_get_all_valid_matlab_roots_from_registry": {
        "one_value_keywords": ["REGISTRY_VIEW"],
    },
    "matlab_get_mex_suffix": {},
    "matlab_get_version_from_matlab_run": {},
    #
    ### FindMFC
    #
    ### FindMotif
    #
    ### FindMPEG2
    #
    ### FindMPEG
    #
    ### FindMPI
    #
    ### FindODBC
    #
    ### FindOpenACC
    #
    ### FindOpenAL
    #
    ### FindOpenCL
    #
    ### FindOpenGL
    #
    ### FindOpenMP
    #
    ### FindOpenSceneGraph
    #
    ### FindOpenSSL
    #
    ### FindOpenThreads
    #
    ### FindosgAnimation
    #
    ### FindosgDB
    #
    ### Findosg_functions
    #
    ### FindosgFX
    #
    ### FindosgGA
    #
    ### FindosgIntrospection
    #
    ### FindosgManipulator
    #
    ### FindosgParticle
    #
    ### FindosgPresentation
    #
    ### FindosgProducer
    #
    ### FindosgQt
    #
    ### Findosg
    #
    ### FindosgShadow
    #
    ### FindosgSim
    #
    ### FindosgTerrain
    #
    ### FindosgText
    #
    ### FindosgUtil
    #
    ### FindosgViewer
    #
    ### FindosgVolume
    #
    ### FindosgWidget
    #
    ### FindPatch
    #
    ### FindPerlLibs
    #
    ### FindPerl
    #
    ### FindPHP4
    #
    ### FindPhysFS
    #
    ### FindPike
    #
    ### FindPkgConfig
    "pkg_check_modules": {
        "options": [
            "REQUIRED",
            "QUIET",
            "NO_CMAKE_PATH",
            "NO_CMAKE_ENVIRONMENT_PATH",
            "IMPORTED_TARGET",
            "GLOBAL",
            "STATIC_TARGET",
        ],
    },
    "pkg_get_variable": {
        "front_positional_arguments": ["<resultVar>", "<moduleName>", "<varName>"],
        "multi_value_keywords": ["DEFINE_VARIABLES"],
    },
    "pkg_search_module": {
        "options": [
            "REQUIRED",
            "QUIET",
            "NO_CMAKE_PATH",
            "NO_CMAKE_ENVIRONMENT_PATH",
            "IMPORTED_TARGET",
            "GLOBAL",
        ],
    },
    #
    ### FindPNG
    #
    ### FindPostgreSQL
    #
    ### FindProducer
    #
    ### FindProtobuf
    "protobuf_generate_cpp": {
        "one_value_keywords": ["DESCRIPTORS", "EXPORT_MACRO"],
    },
    "protobuf_generate_python": {},
    "protobuf_generate": {
        "options": ["APPEND_PATH"],
        "one_value_keywords": [
            "TARGET",
            "LANGUAGE",
            "OUT_VAR",
            "EXPORT_MACRO",
            "PROTOC_OUT_DIR",
            "PLUGIN",
            "PLUGIN_OPTIONS",
            "PROTOC_EXE",
        ],
        "multi_value_keywords": [
            "PROTOS",
            "IMPORT_DIRS",
            "GENERATE_EXTENSIONS",
            "PROTOC_OPTIONS",
            "DEPENDENCIES",
        ],
    },
    #
    ### FindPython
    # (&)
    "python_add_library": {
        "options": ["STATIC", "SHARED", "MODULE", "WITH_SOABI"],
        "one_value_keywords": ["USE_SABI"],
    },
    #
    ### FindPython2
    # (&)
    "python2_add_library": {
        "options": ["STATIC", "SHARED", "MODULE"],
    },
    #
    ### FindPython3
    # (&)
    "python3_add_library": {
        "options": ["STATIC", "SHARED", "MODULE", "WITH_SOABI"],
        "one_value_keywords": ["USE_SABI"],
    },
    #
    ### FindQt3
    #
    ### FindQt4
    "qt4_wrap_cpp": {
        "one_value_keywords": ["TARGET"],
        "multi_value_keywords": ["OPTIONS"],
    },
    "qt4_wrap_ui": {
        "multi_value_keywords": ["OPTIONS"],
    },
    "qt4_add_resources": {
        "multi_value_keywords": ["OPTIONS"],
    },
    "qt4_add_translation": {},
    "qt4_generate_moc": {
        "one_value_keywords": ["TARGET"],
    },
    "qt4_add_dbus_interface": {},
    "qt4_add_dbus_interfaces": {},
    "qt4_add_dbus_adaptor": {},
    "qt4_generate_dbus_interface": {
        "multi_value_keywords": ["OPTIONS"],
    },
    "qt4_create_translation": {
        "multi_value_keywords": ["OPTIONS"],
    },
    "qt4_automoc": {
        "one_value_keywords": ["TARGET"],
    },
    "qt4_use_modules": {},
    #
    ### FindQuickTime
    #
    ### FindRTI
    #
    ### FindRuby
    #
    ### FindSDL_image
    #
    ### FindSDL_mixer
    #
    ### FindSDL_net
    #
    ### FindSDL
    #
    ### FindSDL_sound
    #
    ### FindSDL_ttf
    #
    ### FindSelfPackers
    #
    ### FindSquish
    "squish_add_test": {
        "one_value_keywords": [
            "AUT",
            "SUITE",
            "TEST",
            "SETTINGSGROUP",
            "PRE_COMMAND",
            "POST_COMMAND",
        ],
    },
    #
    ### FindSQLite3
    #
    ### FindSubversion
    "subversion_wc_info": {"options": ["IGNORE_SVN_FAILURE"]},
    "subversion_wc_log": {},
    #
    ### FindSWIG
    #
    ### FindTCL
    #
    ### FindTclsh
    #
    ### FindTclStub
    #
    ### FindThreads
    #
    ### FindTIFF
    #
    ### FindUnixCommands
    #
    ### FindVTK
    #
    ### FindVulkan
    #
    ### FindWget
    #
    ### FindWish
    #
    ### FindwxWidgets
    #
    ### FindXCTest
    "xctest_add_bundle": {},
    "xctest_add_test": {},
    #
    ### FindXalanC
    #
    ### FindXercesC
    #
    ### FindX11
    #
    ### FindXMLRPC
    #
    ### FindZLIB
}


def add_canonical_name(value, canonical_name):
    if isinstance(value, dict):
        value["_canonical_name"] = canonical_name
        return value

    return value


def preprocess_definitions(definitions):
    return make_immutable(
        {
            key.lower(): add_canonical_name(value, key)
            for key, value in definitions.items()
        }
    )


_builtin_commands = preprocess_definitions(builtin_commands)
