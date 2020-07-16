from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .install_command_dumper import Install
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .target_link_libraries_command_dumper import TargetLinkLibraries


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
    options = ["ALL", "VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS"]
    one_value_keywords = ["WORKING_DIRECTORY", "COMMENT", "JOB_POOL"]
    multi_value_keywords = ["COMMAND", "DEPENDS", "BYPRODUCTS", "SOURCES"]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class AddTest(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    options = ["COMMAND_EXPAND_LISTS"]
    one_value_keywords = ["NAME", "WORKING_DIRECTORY"]
    multi_value_keywords = ["COMMAND", "CONFIGURATIONS"]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class BuildCommand(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["CONFIGURATION", "TARGET", "PROJECT_NAME"]


class CreateTestSourcelist(ArgumentAwareCommandInvocationDumper):
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
    one_value_keywords = ["PROPERTY"]
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


class LinkLibraries(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["debug", "optimized", "general"]


class LoadCache(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["READ_WITH_PREFIX"]
    multi_value_keywords = ["EXCLUDE", "INCLUDE_INTERNALS"]


class Project(ArgumentAwareCommandInvocationDumper):
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
    options = ["BEFORE", "SYSTEM"]
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


class TargetSources(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["INTERFACE", "PUBLIC", "PRIVATE"]


class TryCompile(ArgumentAwareCommandInvocationDumper):
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
    ]
    multi_value_keywords = [
        "SOURCES",
        "CMAKE_FLAGS",
        "COMPILE_DEFINITIONS",
        "LINK_OPTIONS",
        "LINK_LIBRARIES",
    ]


class TryRun(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
        "COMPILE_OUTPUT_VARIABLE",
        "RUN_OUTPUT_VARIABLE",
        "OUTPUT_VARIABLE",
    ]
    multi_value_keywords = [
        "CMAKE_FLAGS",
        "COMPILE_DEFINITIONS",
        "LINK_OPTIONS",
        "LINK_LIBRARIES",
        "ARGS",
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
