from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class CTestBuild(ArgumentAwareCommandInvocationDumper):
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


class CTestConfigure(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = [
        "BUILD",
        "SOURCE",
        "OPTIONS",
        "RETURN_VALUE",
        "CAPTURE_CMAKE_ERROR",
    ]


class CTestCoverage(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = ["BUILD", "RETURN_VALUE", "CAPTURE_CMAKE_ERROR"]
    multi_value_keywords = ["LABELS"]


class CTestMemcheck(ArgumentAwareCommandInvocationDumper):
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


class CTestRunScript(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RETURN_VALUE"]


class CTestStart(ArgumentAwareCommandInvocationDumper):
    options = ["APPEND", "QUIET"]
    one_value_keywords = ["GROUP"]


class CTestSubmit(ArgumentAwareCommandInvocationDumper):
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


class CTestTest(ArgumentAwareCommandInvocationDumper):
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


class CTestUpdate(ArgumentAwareCommandInvocationDumper):
    options = ["QUIET"]
    one_value_keywords = ["SOURCE", "RETURN_VALUE", "CAPTURE_CMAKE_ERROR"]


class CTestUpload(ArgumentAwareCommandInvocationDumper):
    options = ["QUIET"]
    one_value_keywords = ["CAPTURE_CMAKE_ERROR"]
    multi_value_keywords = ["FILES"]


ctest_command_mapping = {
    "ctest_build": CTestBuild,
    "ctest_configure": CTestConfigure,
    "ctest_coverage": CTestCoverage,
    "ctest_memcheck": CTestMemcheck,
    "ctest_run_script": CTestRunScript,
    "ctest_start": CTestStart,
    "ctest_submit": CTestSubmit,
    "ctest_test": CTestTest,
    "ctest_update": CTestUpdate,
    "ctest_upload": CTestUpload,
}
