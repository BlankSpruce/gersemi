from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
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
            options=["VERBATIM", "APPEND", "USES_TERMINAL", "COMMAND_EXPAND_LISTS"],
            one_value_keywords=[
                "MAIN_DEPENDENCY",
                "WORKING_DIRECTORY",
                "COMMENT",
                "DEPFILE",
                "JOB_POOL",
            ],
            multi_value_keywords=[
                "OUTPUT",
                "COMMAND",
                "ARGS",
                "DEPENDS",
                "BYPRODUCTS",
                "IMPLICIT_DEPENDS",
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
            one_value_keywords=["TARGET", "WORKING_DIRECTORY", "COMMENT"],
            multi_value_keywords=["COMMAND", "ARGS", "BYPRODUCTS"],
        ),
    }
    keyword_formatters = {"COMMAND": "_format_command_line"}


class AddCustomTarget(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["Name", "ALL"]
    options = ["VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS"]
    one_value_keywords = ["WORKING_DIRECTORY", "COMMENT", "JOB_POOL"]
    multi_value_keywords = ["COMMAND", "DEPENDS", "BYPRODUCTS", "SOURCES"]
    keyword_formatters = {"COMMAND": "_format_command_line"}

    def _format_positional_arguments_group(self, group):
        if len(group) > 1:
            if group[0].children[0] == "ALL":
                first, *rest = group
                return f"{self.visit(first)}\n{super()._format_command_line(rest)}"
        return super()._format_command_line(group)


class AddTest(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    options = ["COMMAND_EXPAND_LISTS"]
    one_value_keywords = ["NAME", "WORKING_DIRECTORY"]
    multi_value_keywords = ["COMMAND", "CONFIGURATIONS"]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class BuildCommand(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["CONFIGURATION", "TARGET", "PROJECT_NAME", "PARALLEL_LEVEL"]


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


class Export(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "EXPORT": dict(one_value_keywords=["EXPORT", "NAMESPACE", "FILE"]),
        "TARGETS": dict(
            options=["APPEND", "EXPORT_LINK_INTERFACE_LIBRARIES"],
            one_value_keywords=["NAMESPACE", "FILE", "ANDROID_MK"],
            multi_value_keywords=["TARGETS"],
        ),
        "PACKAGE": dict(one_value_keywords=["PACKAGE"]),
    }


class IncludeExternalMsProject(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["TYPE", "GUID", "PLATFORM"]


class Install(TwoWordKeywordIsolator, MultipleSignatureCommandInvocationDumper):
    two_words_keywords = [("INCLUDES", "DESTINATION")]

    customized_signatures = {
        "TARGETS": dict(
            options=[
                "ARCHIVE",
                "LIBRARY",
                "RUNTIME",
                "OBJECTS",
                "FRAMEWORK",
                "BUNDLE",
                "PRIVATE_HEADER",
                "PUBLIC_HEADER",
                "RESOURCE",
                "OPTIONAL",
                "EXCLUDE_FROM_ALL",
                "NAMELINK_ONLY",
                "NAMELINK_SKIP",
            ],
            one_value_keywords=[
                "EXPORT",
                "DESTINATION",
                "COMPONENT",
                "NAMELINK_COMPONENT",
                "RUNTIME_DEPENDENCY_SET",
                "FILE_SET",
            ],
            multi_value_keywords=[
                "TARGETS",
                "PERMISSIONS",
                "CONFIGURATIONS",
                "INCLUDES DESTINATION",
                "RUNTIME_DEPENDENCIES",
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
            options=[
                "USE_SOURCE_PERMISSIONS",
                "OPTIONAL",
                "MESSAGE_NEVER",
                "EXCLUDE_FROM_ALL",
                "FILES_MATCHING",
                "EXCLUDE",
            ],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT", "PATTERN", "REGEX"],
            multi_value_keywords=[
                "DIRECTORY",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
                "CONFIGURATIONS",
                "PERMISSIONS",
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
            options=["EXPORT_LINK_INTERFACE_LIBRARIES", "EXCLUDE_FROM_ALL"],
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
            options=[
                "LIBRARY",
                "RUNTIME",
                "FRAMEWORK",
                "BUNDLE",
                "OPTIONAL",
                "EXCLUDE_FROM_ALL",
            ],
            one_value_keywords=["RUNTIME_DEPENDENCY_SET", "DESTINATION", "COMPONENT"],
            multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
        ),
        "RUNTIME_DEPENDENCY_SET": dict(
            options=["LIBRARY", "RUNTIME", "FRAMEWORK", "OPTIONAL", "EXCLUDE_FROM_ALL"],
            one_value_keywords=["DESTINATION", "COMPONENT", "NAMELINK_COMPONENT"],
            multi_value_keywords=[
                "PERMISSIONS",
                "CONFIGURATIONS",
                "PRE_INCLUDE_REGEXES",
                "PRE_EXCLUDE_REGEXES",
                "POST_INCLUDE_REGEXES",
                "POST_EXCLUDE_REGEXES",
                "POST_INCLUDE_FILES",
                "POST_EXCLUDE_FILES",
                "DIRECTORIES",
            ],
        ),
    }


class LinkLibraries(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["debug", "optimized", "general"]


class LoadCache(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["READ_WITH_PREFIX"]
    multi_value_keywords = ["EXCLUDE", "INCLUDE_INTERNALS"]


class Project(ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["<PROJECT-NAME>"]
    one_value_keywords = ["VERSION", "DESCRIPTION", "HOMEPAGE_URL"]
    multi_value_keywords = ["LANGUAGES"]


class SourceGroup(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["REGULAR_EXPRESSION", "TREE", "PREFIX"]
    multi_value_keywords = ["FILES"]


class TargetCompileDefinitions(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetCompileFeatures(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetCompileOptions(ArgumentAwareCommandInvocationDumper):
    options = ["BEFORE"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetIncludeDirectories(ArgumentAwareCommandInvocationDumper):
    options = ["BEFORE", "SYSTEM", "AFTER"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetLinkDirectories(ArgumentAwareCommandInvocationDumper):
    options = ["BEFORE"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetLinkOptions(ArgumentAwareCommandInvocationDumper):
    options = ["BEFORE"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetPrecompileHeaders(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["REUSE_FROM"]
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TargetSources(SectionAwareCommandInvocationDumper):
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
    multi_value_keywords = ["PROPERTIES"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


class SetTargetProperties(
    KeywordWithPairsFormatter, ArgumentAwareCommandInvocationDumper
):
    multi_value_keywords = ["PROPERTIES"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


class SetTestsProperties(
    KeywordWithPairsFormatter, ArgumentAwareCommandInvocationDumper
):
    multi_value_keywords = ["PROPERTIES"]
    keyword_formatters = {"PROPERTIES": "_format_keyword_with_pairs"}


project_command_mapping = {
    "add_custom_command": AddCustomCommand,
    "add_custom_target": AddCustomTarget,
    "add_test": AddTest,
    "build_command": BuildCommand,
    "create_test_sourcelist": CreateTestSourcelist,
    "define_property": DefineProperty,
    "export": Export,
    "include_external_msproject": IncludeExternalMsProject,
    "install": Install,
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
