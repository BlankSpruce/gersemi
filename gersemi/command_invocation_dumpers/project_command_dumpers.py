from typing import List
from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from gersemi.keywords import AnyMatcher, KeywordMatcher
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .section_aware_command_invocation_dumper import SectionAwareCommandInvocationDumper
from .target_link_libraries_command_dumper import TargetLinkLibraries
from .two_word_keyword_isolator import TwoWordKeywordIsolator


class AddCustomCommand(CommandLineFormatter, MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "OUTPUT": dict(
            options=[
                "VERBATIM",
                "APPEND",
                "USES_TERMINAL",
                "COMMAND_EXPAND_LISTS",
                "DEPENDS_EXPLICIT_ONLY",
            ],
            one_value_keywords=[
                "MAIN_DEPENDENCY",
                "WORKING_DIRECTORY",
                "COMMENT",
                "DEPFILE",
                "JOB_POOL",
                "JOB_SERVER_AWARE",
            ],
            multi_value_keywords=[
                "OUTPUT",
                "COMMAND",
                "ARGS",
                "DEPENDS",
                "BYPRODUCTS",
                "IMPLICIT_DEPENDS",
                "OUTPUT",
            ],
        ),
        "TARGET": dict(
            options=[
                "PRE_BUILD",
                "PRE_LINK",
                "POST_BUILD",
                "VERBATIM",
                "USES_TERMINAL",
                "COMMAND_EXPAND_LISTS",
            ],
            one_value_keywords=["TARGET", "WORKING_DIRECTORY", "COMMENT", "TARGET"],
            multi_value_keywords=["COMMAND", "ARGS", "BYPRODUCTS"],
        ),
    }
    keyword_formatters = {
        "COMMAND": "_format_command_line",
        "ARGS": "_format_command_line",
    }


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


class AddDependencies(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]


class AddExecutable(ArgumentAwareCommandInvocationDumper):
    two_words_keywords = [("IMPORTED", "GLOBAL")]
    front_positional_arguments = ["<name>"]
    options = [
        "WIN32",
        "MACOSX_BUNDLE",
        "EXCLUDE_FROM_ALL",
        "IMPORTED",
        "IMPORTED GLOBAL",
    ]
    one_value_keywords = ["ALIAS"]


class AddLibrary(TwoWordKeywordIsolator, ArgumentAwareCommandInvocationDumper):
    two_words_keywords = [("IMPORTED", "GLOBAL")]
    front_positional_arguments = ["<name>"]
    options = [
        "STATIC",
        "SHARED",
        "MODULE",
        "EXCLUDE_FROM_ALL",
        "OBJECT",
        "IMPORTED",
        "IMPORTED GLOBAL",
        "UNKNOWN",
        "INTERFACE",
    ]
    one_value_keywords = ["ALIAS"]


class AddSubdirectory(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["source_dir", "binary_dir"]
    options = ["EXCLUDE_FROM_ALL", "SYSTEM"]


class AddTest(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<name>", "<command>"]
    options = ["COMMAND_EXPAND_LISTS"]
    one_value_keywords = ["NAME", "WORKING_DIRECTORY"]
    multi_value_keywords = ["COMMAND", "CONFIGURATIONS"]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class BuildCommand(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<variable>"]
    one_value_keywords = ["CONFIGURATION", "TARGET", "PROJECT_NAME", "PARALLEL_LEVEL"]


class CMakeFileApi(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "QUERY": dict(
            options=["QUERY"],
            one_value_keywords=["API_VERSION"],
            multi_value_keywords=["CODEMODEL", "CACHE", "CMAKEFILES", "TOOLCHAINS"],
        ),
    }


class CreateTestSourcelist(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["sourceListName", "driverName"]
    one_value_keywords = ["EXTRA_INCLUDE", "FUNCTION"]


class DefineProperty(ArgumentAwareCommandInvocationDumper):
    options = [
        "GLOBAL",
        "DIRECTORY",
        "TARGET",
        "SOURCE",
        "TEST",
        "VARIABLE",
        "CACHED_VARIABLE",
        "INHERITED",
    ]
    one_value_keywords = ["PROPERTY", "INITIALIZE_FROM_VARIABLE"]
    multi_value_keywords = ["BRIEF_DOCS", "FULL_DOCS"]


class Export(
    SectionAwareCommandInvocationDumper, MultipleSignatureCommandInvocationDumper
):
    customized_signatures = {
        "EXPORT": dict(
            options=["EXPORT_PACKAGE_DEPENDENCIES"],
            one_value_keywords=["EXPORT", "NAMESPACE", "FILE"],
        ),
        "TARGETS": dict(
            options=["APPEND", "EXPORT_LINK_INTERFACE_LIBRARIES"],
            one_value_keywords=["NAMESPACE", "FILE", "ANDROID_MK"],
            multi_value_keywords=["TARGETS"],
        ),
        "PACKAGE": dict(one_value_keywords=["PACKAGE"]),
        "SETUP": dict(
            one_value_keywords=["SETUP"],
            multi_value_keywords=["PACKAGE_DEPENDENCY", "TARGET"],
            sections=dict(
                PACKAGE_DEPENDENCY=dict(
                    front_positional_arguments=["<dep>"],
                    one_value_keywords=["ENABLED"],
                    multi_value_keywords=["EXTRA_ARGS"],
                ),
                TARGET=dict(
                    front_positional_arguments=["<target>"],
                    one_value_keywords=["XCFRAMEWORK_LOCATION"],
                ),
            ),
        ),
    }


class FtlkWrapUi(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["resultingLibraryName"]


class GetSourceFileProperty(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<variable>", "<file>"]
    back_positional_arguments = ["<property>"]
    one_value_keywords = ["DIRECTORY", "TARGET_DIRECTORY"]


class GetTargetProperty(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<VAR>", "target", "property"]


class GetTestProperty(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["test", "property"]
    one_value_keywords = ["DIRECTORY"]


class IncludeDirectories(ArgumentAwareCommandInvocationDumper):
    options = ["AFTER", "BEFORE", "SYSTEM"]


class IncludeExternalMsProject(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["projectname", "location"]
    one_value_keywords = ["TYPE", "GUID", "PLATFORM"]


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


class Install(
    TwoWordKeywordIsolator,
    SectionAwareCommandInvocationDumper,
    MultipleSignatureCommandInvocationDumper,
):
    two_words_keywords = [
        _INCLUDES_DESTINATION,
        _FILE_SET_Any,
        _PATTERN_Any,
        _REGEX_Any,
    ]

    customized_signatures = {
        "TARGETS": dict(
            sections={
                kind: dict(
                    options=[
                        "OPTIONAL",
                        "EXCLUDE_FROM_ALL",
                        "NAMELINK_ONLY",
                        "NAMELINK_SKIP",
                    ],
                    one_value_keywords=[
                        "DESTINATION",
                        "COMPONENT",
                        "NAMELINK_COMPONENT",
                    ],
                    multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
                )
                for kind in _Install_TARGETS_kinds
            },
            one_value_keywords=[
                "EXPORT",
                "RUNTIME_DEPENDENCY_SET",
            ],
            multi_value_keywords=[
                "TARGETS",
                _INCLUDES_DESTINATION,
                "RUNTIME_DEPENDENCIES",
                *_Install_TARGETS_kinds,
            ],
        ),
        "FILES": dict(
            options=["OPTIONAL", "EXCLUDE_FROM_ALL"],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT", "RENAME"],
            multi_value_keywords=["FILES", "PERMISSIONS", "CONFIGURATIONS"],
        ),
        "PROGRAMS": dict(
            options=["OPTIONAL", "EXCLUDE_FROM_ALL"],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT", "RENAME"],
            multi_value_keywords=["PROGRAMS", "PERMISSIONS", "CONFIGURATIONS"],
        ),
        "DIRECTORY": dict(
            sections={
                kind: dict(options=["EXCLUDE"], multi_value_keywords=["PERMISSIONS"])
                for kind in _Install_DIRECTORY_kinds
            },
            options=[
                "USE_SOURCE_PERMISSIONS",
                "OPTIONAL",
                "MESSAGE_NEVER",
                "EXCLUDE_FROM_ALL",
                "FILES_MATCHING",
            ],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT"],
            multi_value_keywords=[
                "DIRECTORY",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
                "CONFIGURATIONS",
                *_Install_DIRECTORY_kinds,
            ],
        ),
        "SCRIPT": dict(
            options=["EXCLUDE_FROM_ALL", "ALL_COMPONENTS"],
            one_value_keywords=["SCRIPT", "COMPONENT"],
        ),
        "CODE": dict(
            options=["EXCLUDE_FROM_ALL", "ALL_COMPONENTS"],
            one_value_keywords=["CODE", "COMPONENT"],
        ),
        "EXPORT": dict(
            options=[
                "EXPORT_LINK_INTERFACE_LIBRARIES",
                "EXCLUDE_FROM_ALL",
                "EXPORT_PACKAGE_DEPENDENCIES",
            ],
            one_value_keywords=[
                "EXPORT",
                "DESTINATION",
                "NAMESPACE",
                "FILE",
                "COMPONENT",
            ],
            multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
        ),
        "EXPORT_ANDROID_MK": dict(
            options=["EXPORT_LINK_INTERFACE_LIBRARIES", "EXCLUDE_FROM_ALL"],
            one_value_keywords=[
                "EXPORT_ANDROID_MK",
                "DESTINATION",
                "NAMESPACE",
                "FILE",
                "COMPONENT",
            ],
            multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
        ),
        "IMPORTED_RUNTIME_ARTIFACTS": dict(
            sections={
                kind: dict(
                    options=["OPTIONAL", "EXCLUDE_FROM_ALL"],
                    one_value_keywords=["DESTINATION", "COMPONENT"],
                    multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
                )
                for kind in _Install_IMPORTED_RUNTIME_ARTIFACTS_kinds
            },
            one_value_keywords=["RUNTIME_DEPENDENCY_SET"],
            multi_value_keywords=[
                "IMPORTED_RUNTIME_ARTIFACTS",
                *_Install_IMPORTED_RUNTIME_ARTIFACTS_kinds,
            ],
        ),
        "RUNTIME_DEPENDENCY_SET": dict(
            sections={
                kind: dict(
                    options=["OPTIONAL", "EXCLUDE_FROM_ALL"],
                    one_value_keywords=[
                        "DESTINATION",
                        "COMPONENT",
                        "NAMELINK_COMPONENT",
                    ],
                    multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
                )
                for kind in _Install_RUNTIME_DEPENDENCY_SET_kinds
            },
            options=[
                "LIBRARY",
                "RUNTIME",
                "FRAMEWORK",
            ],
            multi_value_keywords=[
                "PRE_INCLUDE_REGEXES",
                "PRE_EXCLUDE_REGEXES",
                "POST_INCLUDE_REGEXES",
                "POST_EXCLUDE_REGEXES",
                "POST_INCLUDE_FILES",
                "POST_EXCLUDE_FILES",
                "DIRECTORIES",
                *_Install_RUNTIME_DEPENDENCY_SET_kinds,
            ],
        ),
    }


class LinkDirectories(ArgumentAwareCommandInvocationDumper):
    options = ["AFTER", "BEFORE"]


class LinkLibraries(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["debug", "optimized", "general"]


class LoadCache(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["pathToBuildDirectory"]
    one_value_keywords = ["READ_WITH_PREFIX"]
    multi_value_keywords = ["EXCLUDE", "INCLUDE_INTERNALS"]


class Project(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<PROJECT-NAME>"]
    one_value_keywords = ["VERSION", "DESCRIPTION", "HOMEPAGE_URL"]
    multi_value_keywords = ["LANGUAGES"]


class SourceGroup(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<name>"]
    one_value_keywords = ["REGULAR_EXPRESSION", "TREE", "PREFIX"]
    multi_value_keywords = ["FILES"]


class TargetCompileDefinitions(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetCompileFeatures(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetCompileOptions(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    options = ["BEFORE"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetIncludeDirectories(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    options = ["BEFORE", "SYSTEM", "AFTER"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetLinkDirectories(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    options = ["BEFORE"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetLinkOptions(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    options = ["BEFORE"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetPrecompileHeaders(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    one_value_keywords = ["REUSE_FROM"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetSources(SectionAwareCommandInvocationDumper):
    front_positional_arguments = ["<target>"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]
    sections = {
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
    }


class TryCompile(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = [
        "<compileResultVar>",
        "<bindir>",
        "<srcdir>",  # or "<srcfile>"
        "<projectName>",
        "<targetName>",
    ]
    option = ["NO_CACHE", "NO_LOG"]
    one_value_keywords = [
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
    ]
    multi_value_keywords = [
        "SOURCES",
        "CMAKE_FLAGS",
        "COMPILE_DEFINITIONS",
        "LINK_OPTIONS",
        "LINK_LIBRARIES",
        "SOURCE_FROM_CONTENT",
        "SOURCE_FROM_VAR",
        "SOURCE_FROM_FILE",
    ]


class TryRun(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = [
        "<runResultVar>",
        "<compileResultVar>",
        "<bindir>",
        "<srcfile>",
    ]
    options = ["NO_CACHE", "NO_LOG"]
    one_value_keywords = [
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
    ]
    multi_value_keywords = [
        "CMAKE_FLAGS",
        "COMPILE_DEFINITIONS",
        "LINK_OPTIONS",
        "LINK_LIBRARIES",
        "ARGS",
        "SOURCES",
        "SOURCE_FROM_CONTENT",
        "SOURCE_FROM_VAR",
        "SOURCE_FROM_FILE",
    ]


class SetSourceFilesProperties(
    KeywordWithPairsFormatter, ArgumentAwareCommandInvocationDumper
):
    multi_value_keywords = ["PROPERTIES", "DIRECTORY", "TARGET_DIRECTORY"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


class SetTargetProperties(
    KeywordWithPairsFormatter, ArgumentAwareCommandInvocationDumper
):
    multi_value_keywords = ["PROPERTIES"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


class SetTestsProperties(
    KeywordWithPairsFormatter, ArgumentAwareCommandInvocationDumper
):
    one_value_keywords = ["DIRECTORY"]
    multi_value_keywords = ["PROPERTIES"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


project_command_mapping = {
    "add_custom_command": AddCustomCommand,
    "add_custom_target": AddCustomTarget,
    "add_dependencies": AddDependencies,
    "add_executable": AddExecutable,
    "add_library": AddLibrary,
    "add_subdirectory": AddSubdirectory,
    "add_test": AddTest,
    "build_command": BuildCommand,
    "cmake_file_api": CMakeFileApi,
    "create_test_sourcelist": CreateTestSourcelist,
    "define_property": DefineProperty,
    "export": Export,
    "fltk_wrap_ui": FtlkWrapUi,
    "get_source_file_property": GetSourceFileProperty,
    "get_target_property": GetTargetProperty,
    "get_test_property": GetTestProperty,
    "include_directories": IncludeDirectories,
    "include_external_msproject": IncludeExternalMsProject,
    "install": Install,
    "link_directories": LinkDirectories,
    "link_libraries": LinkLibraries,
    "load_cache": LoadCache,
    "project": Project,
    "source_group": SourceGroup,
    "set_source_files_properties": SetSourceFilesProperties,
    "set_target_properties": SetTargetProperties,
    "set_tests_properties": SetTestsProperties,
    "target_compile_definitions": TargetCompileDefinitions,
    "target_compile_features": TargetCompileFeatures,
    "target_compile_options": TargetCompileOptions,
    "target_include_directories": TargetIncludeDirectories,
    "target_link_directories": TargetLinkDirectories,
    "target_link_libraries": TargetLinkLibraries,
    "target_link_options": TargetLinkOptions,
    "target_precompile_headers": TargetPrecompileHeaders,
    "target_sources": TargetSources,
    "try_compile": TryCompile,
    "try_run": TryRun,
}
