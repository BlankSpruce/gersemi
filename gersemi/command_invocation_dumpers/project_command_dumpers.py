from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)


class AddCustomCommandCommandDumper(MultipleSignatureCommandInvocationDumper):
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


class AddTestCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["COMMAND_EXPAND_LISTS"]
    one_value_keywords = ["NAME", "WORKING_DIRECTORY"]
    multi_value_keywords = ["COMMAND", "CONFIGURATIONS"]


class BuildCommandCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["CONFIGURATION", "TARGET", "PROJECT_NAME"]


class ExportCommandDumper(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "EXPORT": dict(one_value_keywords=["EXPORT", "NAMESPACE", "FILE"]),
        "TARGETS": dict(
            options=["APPEND", "EXPORT_LINK_INTERFACE_LIBRARIES"],
            one_value_keywords=["NAMESPACE", "FILE", "ANDROID_MK"],
            multi_value_keywords=["TARGETS"],
        ),
        "PACKAGE": dict(one_value_keywords=["PACKAGE"]),
    }


class IncludeExternalMsProjectCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["TYPE", "GUID", "PLATFORM"]


class LinkLibrariesCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["debug", "optimized", "general"]


class LoadCacheCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["READ_WITH_PREFIX"]
    multi_value_keywords = ["EXCLUDE", "INCLUDE_INTERNALS"]


class ProjectCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["VERSION", "DESCRIPTION", "HOMEPAGE_URL"]
    multi_value_keywords = ["LANGUAGES"]


project_command_mapping = {
    "add_custom_command": AddCustomCommandCommandDumper,
    "add_test": AddTestCommandDumper,
    "build_command": BuildCommandCommandDumper,
    "export": ExportCommandDumper,
    "include_external_msproject": IncludeExternalMsProjectCommandDumper,
    "link_libraries": LinkLibrariesCommandDumper,
    "load_cache": LoadCacheCommandDumper,
    "project": ProjectCommandDumper,
}
