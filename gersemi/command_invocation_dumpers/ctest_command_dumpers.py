from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class CTestBuildCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = [
        "BUILD",
        "CONFIGURATION",
        "FLAGS",
        "PROJECT_NAME",
        "TARGET",
        "NUMBER_ERRORS",
        "NUMBER_WARNINGS",
        "RETURN_VALUE",
        "CAPTURE_CMAKE_ERROR",
    ]


class CTestConfigureCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = [
        "BUILD",
        "SOURCE",
        "OPTIONS",
        "RETURN_VALUE",
        "CAPTURE_CMAKE_ERROR",
    ]


class CTestCoverageCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = ["BUILD", "RETURN_VALUE", "CAPTURE_CMAKE_ERROR"]
    multi_value_keywords = ["LABELS"]


class CTestMemcheckCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = [
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
    ]


class CTestRunScriptCommandDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RETURN_VALUE"]


class CTestStartCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = ["GROUP"]


class CTestSubmitCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["QUIET"]
    one_value_keywords = [
        "SUBMIT_URL",
        "BUILD_ID",
        "HTTPHEADER",
        "RETRY_COUNT",
        "RETRY_DELAY",
        "RETURN_VALUE",
        "CAPTURE_CMAKE_ERROR",
        "CDASH_UPLOAD",
        "CDASH_UPLOAD_TYPE",
    ]
    multi_value_keywords = ["PARTS", "FILES"]


class CTestTestCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = [
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
    ]


class CTestUpdateCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["QUIET"]
    one_value_keywords = ["SOURCE", "RETURN_VALUE", "CAPTURE_CMAKE_ERROR"]


class CTestUploadCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["QUIET"]
    one_value_keywords = ["CAPTURE_CMAKE_ERROR"]
    multi_value_keywords = ["FILES"]


ctest_command_mapping = {
    "ctest_build": CTestBuildCommandDumper,
    "ctest_configure": CTestConfigureCommandDumper,
    "ctest_coverage": CTestCoverageCommandDumper,
    "ctest_memcheck": CTestMemcheckCommandDumper,
    "ctest_run_script": CTestRunScriptCommandDumper,
    "ctest_start": CTestStartCommandDumper,
    "ctest_submit": CTestSubmitCommandDumper,
    "ctest_test": CTestTestCommandDumper,
    "ctest_update": CTestUpdateCommandDumper,
    "ctest_upload": CTestUploadCommandDumper,
}
