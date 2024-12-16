from typing import Iterable, List, Mapping
from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keywords import AnyMatcher, KeywordMatcher
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class AddCustomTarget(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["Name"]
    options = ["ALL", "VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS"]
    one_value_keywords = [
        "WORKING_DIRECTORY",
        "COMMENT",
        "JOB_POOL",
        "JOB_SERVER_AWARE",
    ]
    multi_value_keywords = ["COMMAND", "DEPENDS", "BYPRODUCTS", "SOURCES"]
    keyword_formatters = {"COMMAND": "_format_command_line"}

    def positional_arguments(self, tree):
        if len(tree.children) > 1:
            return super()._format_command_line(tree.children)
        return super().positional_arguments(tree)


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

project_command_mapping = {
    "add_custom_command": {
        "customized_signatures": {
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
            },
        },
        "keyword_formatters": {
            "COMMAND": "_format_command_line",
            "ARGS": "_format_command_line",
        },
    },
    "add_custom_target": AddCustomTarget,
    "add_dependencies": {
        "front_positional_arguments": ["<target>"],
    },
    "add_executable": {
        "two_words_keywords": [("IMPORTED", "GLOBAL")],
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
        "two_words_keywords": [("IMPORTED", "GLOBAL")],
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
    "add_subdirectory": {
        "front_positional_arguments": ["source_dir", "binary_dir"],
        "options": ["EXCLUDE_FROM_ALL", "SYSTEM"],
    },
    "add_test": {
        "front_positional_arguments": ["<name>", "<command>"],
        "options": ["COMMAND_EXPAND_LISTS"],
        "one_value_keywords": ["NAME", "WORKING_DIRECTORY"],
        "multi_value_keywords": ["COMMAND", "CONFIGURATIONS"],
        "keyword_formatters": {"COMMAND": "_format_command_line"},
    },
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
        "customized_signatures": {
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
    "export": {
        "customized_signatures": {
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
    "install": {
        "two_words_keywords": [
            _INCLUDES_DESTINATION,
            _FILE_SET_Any,
            _PATTERN_Any,
            _REGEX_Any,
        ],
        "customized_signatures": {
            "TARGETS": {
                "sections": {
                    kind: {
                        "options": [
                            "OPTIONAL",
                            "EXCLUDE_FROM_ALL",
                            "NAMELINK_ONLY",
                            "NAMELINK_SKIP",
                        ],
                        "one_value_keywords": [
                            "DESTINATION",
                            "COMPONENT",
                            "NAMELINK_COMPONENT",
                        ],
                        "multi_value_keywords": ["PERMISSIONS", "CONFIGURATIONS"],
                    }
                    for kind in _Install_TARGETS_kinds
                },
                "one_value_keywords": [
                    "EXPORT",
                    "RUNTIME_DEPENDENCY_SET",
                ],
                "multi_value_keywords": [
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
                "options": [
                    "LIBRARY",
                    "RUNTIME",
                    "FRAMEWORK",
                ],
                "multi_value_keywords": [
                    "PRE_INCLUDE_REGEXES",
                    "PRE_EXCLUDE_REGEXES",
                    "POST_INCLUDE_REGEXES",
                    "POST_EXCLUDE_REGEXES",
                    "POST_INCLUDE_FILES",
                    "POST_EXCLUDE_FILES",
                    "DIRECTORIES",
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
        "one_value_keywords": ["VERSION", "DESCRIPTION", "HOMEPAGE_URL"],
        "multi_value_keywords": ["LANGUAGES"],
    },
    "source_group": {
        "front_positional_arguments": ["<name>"],
        "one_value_keywords": ["REGULAR_EXPRESSION", "TREE", "PREFIX"],
        "multi_value_keywords": ["FILES"],
    },
    "set_source_files_properties": {
        "multi_value_keywords": ["PROPERTIES", "DIRECTORY", "TARGET_DIRECTORY"],
        "keyword_formatters": {"PROPERTIES": "_format_keyword_with_pairs"},
    },
    "set_target_properties": {
        "multi_value_keywords": ["PROPERTIES"],
        "keyword_formatters": {"PROPERTIES": "_format_keyword_with_pairs"},
    },
    "set_tests_properties": {
        "one_value_keywords": ["DIRECTORY"],
        "multi_value_keywords": ["PROPERTIES"],
        "keyword_formatters": {
            "PROPERTIES": "_format_keyword_with_pairs",
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
        "front_positional_arguments": ["<target>"],
        "multi_value_keywords": ["INTERFACE", "PUBLIC", "PRIVATE"],
        "sections": {
            "INTERFACE": {
                "one_value_keywords": ["FILE_SET", "TYPE"],
                "multi_value_keywords": ["BASE_DIRS", "FILES"],
            },
            "PUBLIC": {
                "one_value_keywords": ["FILE_SET", "TYPE"],
                "multi_value_keywords": ["BASE_DIRS", "FILES"],
            },
            "PRIVATE": {
                "one_value_keywords": ["FILE_SET", "TYPE"],
                "multi_value_keywords": ["BASE_DIRS", "FILES"],
            },
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
}
