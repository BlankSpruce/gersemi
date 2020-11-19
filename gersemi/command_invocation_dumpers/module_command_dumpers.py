from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class AndroidAddTestData(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
        "FILES_DEST",
        "LIBS_DEST",
        "DEVICE_OBJECT_STORE",
        "DEVICE_TEST_DIR",
    ]
    multi_value_keywords = ["FILES", "LIBS", "NO_LINK_REGEX"]


class CheckCSourceCompiles(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["FAIL_REGEX"]


class CheckCXXSourceCompiles(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["FAIL_REGEX"]


class CheckFortranSourceCompiles(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["SRC_EXT"]
    multi_value_keywords = ["FAIL_REGEX"]


class CheckFortranSourceRuns(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["SRC_EXT"]


class CheckIPOSupported(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["RESULT", "OUTPUT"]
    multi_value_keywords = ["LANGUAGES"]


class CheckIncludeFiles(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["LANGUAGE"]


class CheckOBJCSourceCompiles(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["FAIL_REGEX"]


class CheckOBJCXXSourceCompiles(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["FAIL_REGEX"]


class CheckPIESupported(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["OUTPUT_VARIABLE"]
    multi_value_keywords = ["LANGUAGES"]


class CheckStructHasMember(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["LANGUAGE"]


class CheckTypeSize(ArgumentAwareCommandInvocationDumper):
    options = ["BUILTIN_TYPES_ONLY"]
    one_value_keywords = ["LANGUAGE"]


class CMakeAddFortranSubdirectory(
    CommandLineFormatter, ArgumentAwareCommandInvocationDumper
):
    options = ["NO_EXTERNAL_INSTALL", "LINK_LIBRARIES"]
    one_value_keywords = ["PROJECT", "ARCHIVE_DIR", "RUNTIME_DIR"]
    multi_value_keywords = ["LIBRARIES", "LINK_LIBS", "CMAKE_COMMAND_LINE"]
    keyword_formatters = {"CMAKE_COMMAND_LINE": "_format_command_line"}


class CMakePrintProprties(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = [
        "TARGETS",
        "SOURCES",
        "DIRECTORIES",
        "TESTS",
        "CACHE_ENTRIES",
        "PROPERTIES",
    ]


class ConfigurePackageConfigFile(ArgumentAwareCommandInvocationDumper):
    options = ["NO_SET_AND_CHECK_MACRO", "NO_CHECK_REQUIRED_COMPONENTS_MACRO"]
    one_value_keywords = ["INSTALL_DESTINATION", "INSTALL_PREFIX"]
    multi_value_keywords = ["PATH_VARS"]


class CPackAddComponent(ArgumentAwareCommandInvocationDumper):
    options = ["HIDDEN", "REQUIRED", "DISABLED", "DOWNLOADED"]
    one_value_keywords = [
        "DISPLAY_NAME",
        "DESCRIPTION",
        "GROUP",
        "ARCHIVE_FILE",
        "PLIST",
    ]
    multi_value_keywords = ["DEPENDS", "INSTALL_TYPES"]


class CPackAddComponentGroup(ArgumentAwareCommandInvocationDumper):
    options = ["EXPANDED", "BOLD_TITLE"]
    one_value_keywords = ["DISPLAY_NAME", "DESCRIPTION", "PARENT_GROUP"]


class CPackAddInstallType(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DISPLAY_NAME"]


class CPackConfigureDownloads(ArgumentAwareCommandInvocationDumper):
    options = ["ALL", "ADD_REMOVE", "NO_ADD_REMOVE"]
    one_value_keywords = ["UPLOAD_DIRECTORY"]


class CPackIFWAddRepository(ArgumentAwareCommandInvocationDumper):
    options = ["DISABLED"]
    one_value_keywords = ["URL", "USERNAME", "PASSWORD", "DISPLAY_NAME"]


class CPackIFWConfigureComponent(ArgumentAwareCommandInvocationDumper):
    options = [
        "COMMON",
        "ESSENTIAL",
        "VIRTUAL",
        "FORCED_INSTALLATION",
        "REQUIRES_ADMIN_RIGHTS",
    ]
    one_value_keywords = [
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
    ]
    multi_value_keywords = [
        "DEPENDS",
        "DEPENDENCIES",
        "AUTO_DEPEND_ON",
        "LICENSES",
        "USER_INTERFACES",
        "TRANSLATIONS",
        "REPLACES",
    ]


class CPackIFWConfigureComponentGroup(ArgumentAwareCommandInvocationDumper):
    options = [
        "VIRTUAL",
        "FORCED_INSTALLATION",
        "REQUIRES_ADMIN_RIGHTS",
    ]

    one_value_keywords = [
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
    ]
    multi_value_keywords = [
        "DEPENDS",
        "DEPENDENCIES",
        "AUTO_DEPEND_ON",
        "LICENSES",
        "USER_INTERFACES",
        "TRANSLATIONS",
        "REPLACES",
    ]


class CPackIFWUpdateRepository(ArgumentAwareCommandInvocationDumper):
    options = ["ADD", "REMOVE", "REPLACE", "DISABLED"]
    one_value_keywords = [
        "URL",
        "OLD_URL",
        "NEW_URL",
        "USERNAME",
        "PASSWORD",
        "DISPLAY_NAME",
    ]


class CTestCoverageCollectGCOV(
    CommandLineFormatter, ArgumentAwareCommandInvocationDumper
):
    options = ["GLOB", "DELETE", "QUIET"]
    one_value_keywords = ["TARBALL", "SOURCE", "BUILD", "GCOV_COMMAND"]
    multi_value_keywords = ["GCOV_OPTIONS"]
    keyword_formatters = {"GCOV_OPTIONS": "_format_command_line"}


class ExternalProjectAdd(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
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
        # Configure Step
        "CMAKE_COMMAND",
        "CMAKE_GENERATOR",
        "CMAKE_GENERATOR_PLATFORM",
        "CMAKE_GENERATOR_TOOLSET",
        "CMAKE_GENERATOR_INSTANCE",
        "SOURCE_SUBDIR",
        # Build Step
        "BUILD_IN_SOURCE",
        "BUILD_ALWAYS",
        # Install Step
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
        "USES_TERMINAL_CONFIGURE",
        "USES_TERMINAL_BUILD",
        "USES_TERMINAL_INSTALL",
        "USES_TERMINAL_TEST",
        # Target
        "EXCLUDE_FROM_ALL",
        # Miscellaneous
        "LIST_SEPARATOR",
    ]
    multi_value_keywords = [
        # Download Step
        "DOWNLOAD_COMMAND",
        "URL",
        "HTTP_HEADER",
        "GIT_SUBMODULES",
        "GIT_CONFIG",
        # Update/Patch Step
        "UPDATE_COMMAND",
        "PATCH_COMMAND",
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
    ]
    keyword_formatters = {
        key: "_format_command_line"
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
    }


class ExternalProjectAddStep(
    CommandLineFormatter, ArgumentAwareCommandInvocationDumper
):
    one_value_keywords = [
        "COMMENT",
        "ALWAYS",
        "EXCLUDE_FROM_MAIN",
        "WORKING_DIRECTORY",
        "LOG",
        "USES_TERMINAL",
    ]
    multi_value_keywords = [
        "COMMAND",
        "DEPENDEES",
        "DEPENDERS",
        "DEPENDS",
        "BYPRODUCTS",
    ]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class FeatureSummary(ArgumentAwareCommandInvocationDumper):
    options = [
        "APPEND",
        "INCLUDE_QUIET_PACKAGES",
        "FATAL_ON_MISSING_REQUIRED_PACKAGES",
        "QUIET_ON_EMPTY",
        "DEFAULT_DESCRIPTION",
    ]
    one_value_keywords = ["FILENAME", "VAR", "DESCRIPTION", "WHAT"]


class SetPackageProperties(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["URL", "DESCRIPTION", "TYPE", "PURPOSE"]


class FetchContentDeclare(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
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
        "SOURCE_SUBDIR",
        # Update/Patch Step
        "UPDATE_DISCONNECTED",
    ]
    multi_value_keywords = [
        # Download Step
        "DOWNLOAD_COMMAND",
        "URL",
        "HTTP_HEADER",
        "GIT_SUBMODULES",
        "GIT_CONFIG",
        # Update/Patch Step
        "UPDATE_COMMAND",
        "PATCH_COMMAND",
    ]
    keyword_formatters = {
        key: "_format_command_line"
        for key in ["DOWNLOAD_COMMAND", "UPDATE_COMMAND", "PATCH_COMMAND"]
    }


class FetchContentPopulate(ArgumentAwareCommandInvocationDumper):
    options = ["QUIET"]
    one_value_keywords = [
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
    ]
    multi_value_keywords = [
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
    ]


class FetchContentGetProperties(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["SOURCE_DIR", "BINARY_DIR", "POPULATED"]


class FindPackageHandleStandardArgs(ArgumentAwareCommandInvocationDumper):
    options = ["HANDLE_COMPONENTS", "CONFIG_MODE", "NAME_MISMATCHED"]
    one_value_keywords = [
        "FOUND_VAR",
        "VERSION_VAR",
        "REASON_FAILURE_MESSAGE",
        "FAIL_MESSAGE",
    ]
    multi_value_keywords = ["REQUIRED_VARS"]


class FindPackageCheckVersion(ArgumentAwareCommandInvocationDumper):
    options = ["HANDLE_VERSION_RANGE"]
    one_value_keywords = ["RESULT_MESSAGE_VARIABLE"]


class FortranCInterfaceHeader(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["MACRO_NAMESPACE", "SYMBOL_NAMESPACE"]
    multi_value_keywords = ["SYMBOLS"]


class GenerateExportHeader(ArgumentAwareCommandInvocationDumper):
    options = ["DEFINE_NO_DEPRECATED"]
    one_value_keywords = [
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
    ]


class GTestAddTests(ArgumentAwareCommandInvocationDumper):
    options = ["SKIP_DEPENDENCY"]
    one_value_keywords = [
        "TARGET",
        "WORKING_DIRECTORY",
        "TEST_PREFIX",
        "TEST_SUFFIX",
        "TEST_LIST",
    ]
    multi_value_keywords = ["SOURCES", "EXTRA_ARGS"]


class GTestDiscoverTests(
    CommandLineFormatter,
    KeywordWithPairsFormatter,
    ArgumentAwareCommandInvocationDumper,
):
    options = ["NO_PRETTY_TYPES", "NO_PRETTY_VALUES"]
    one_value_keywords = [
        "WORKING_DIRECTORY",
        "TEST_PREFIX",
        "TEST_SUFFIX",
        "TEST_LIST",
        "DISCOVERY_TIMEOUT",
        "XML_OUTPUT_DIR",
        "DISCOVERY_MODE",
    ]
    multi_value_keywords = ["EXTRA_ARGS", "PROPERTIES"]
    keyword_formatters = {
        "EXTRA_ARGS": "_format_command_line",
        "PROPERTIES": "_format_keyword_with_pairs",
    }


class AddJar(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
        "ENTRY_POINT",
        "VERSION",
        "OUTPUT_NAME",
        "OUTPUT_DIR",
        "GENERATE_NATIVE_HEADERS",
        "DESTINATION",
    ]
    multi_value_keywords = ["SOURCES", "INCLUDE_JARS"]


class InstallJar(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DESTINATION", "COMPONENT"]


class InstallJniSymlink(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DESTINATION", "COMPONENT"]


class InstallJarExports(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["NAMESPACE", "FILE", "DESTINATION", "COMPONENT"]
    multi_value_keywords = ["TARGETS"]


class ExportJars(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["NAMESPACE", "FILE"]
    multi_value_keywords = ["TARGETS"]


class FindJar(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DOC", "ENV"]
    multi_value_keywords = ["NAMES", "PATHS", "VERSIONS"]


class CreateJavaDoc(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
        "SOURCEPATH",
        "CLASSPATH",
        "INSTALLPATH",
        "DOCTITLE",
        "WINDOWTITLE",
        "AUTHOR",
        "USE",
        "VERSION",
    ]
    multi_value_keywords = ["PACKAGES", "FILES"]


class CreateJavah(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["TARGET", "GENERATED_FILES", "OUTPUT_NAME", "OUTPUT_DIR"]
    multi_value_keywords = ["CLASSES", "CLASSPATH", "DEPENDS"]


class SwigAddLibrary(ArgumentAwareCommandInvocationDumper):
    options = ["NO_PROXY"]
    one_value_keywords = ["TYPE", "LANGUAGE", "OUTPUT_DIR", "OUTFILE_DIR"]
    multi_value_keywords = ["SOURCES"]


class WriteCompilerDetectionHeader(ArgumentAwareCommandInvocationDumper):
    options = ["ALLOW_UNKNOWN_COMPILERS", "ALLOW_UNKNOWN_COMPILER_VERSIONS"]
    one_value_keywords = [
        "FILE",
        "PREFIX",
        "OUTPUT_FILES_VAR",
        "OUTPUT_DIR",
        "VERSION",
        "PROLOG",
        "EPILOG",
    ]
    multi_value_keywords = ["COMPILERS", "FEATURES", "BARE_FEATURES"]


class WriteBasicPackageVersionFile(ArgumentAwareCommandInvocationDumper):
    options = ["ARCH_INDEPENDENT"]
    one_value_keywords = ["VERSION", "COMPATIBILITY"]


class BisonTarget(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["COMPILE_FLAGS", "DEFINES_FILES", "VERBOSE", "REPORT_FILE"]


class DoxygenAddDocs(ArgumentAwareCommandInvocationDumper):
    options = ["ALL", "USE_STAMP_FILE"]
    one_value_keywords = ["WORKING_DIRECTORY", "COMMENT"]


class EnvModule(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["OUTPUT_VARIABLE", "RESULT_VARIABLE"]
    multi_value_keywords = ["COMMAND"]
    keyword_formatters = {"COMMAND": "_format_command_line"}


class EnvModuleSwap(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["OUTPUT_VARIABLE", "RESULT_VARIABLE"]


class FlexTarget(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["COMPILE_FLAGS", "DEFINES_FILES"]


class GettextCreateTranslations(ArgumentAwareCommandInvocationDumper):
    options = ["ALL"]


class GettextProcessPotFile(ArgumentAwareCommandInvocationDumper):
    options = ["ALL"]
    one_value_keywords = ["INSTALL_DESTINATION"]
    multi_value_keywords = ["LANGUAGES"]


class GettextProcessPoFiles(ArgumentAwareCommandInvocationDumper):
    options = ["ALL"]
    one_value_keywords = ["INSTALL_DESTINATION"]
    multi_value_keywords = ["PO_FILES"]


class MatlabAddUnitTest(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    options = ["NO_UNITTEST_FRAMEWORK"]
    one_value_keywords = [
        "NAME",
        "UNITTEST_FILE",
        "CUSTOM_TEST_COMMAND",
        "UNITTEST_PRECOMMAND",
        "TIMEOUT",
    ]
    multi_value_keywords = [
        "ADDITIONAL_PATH",
        "MATLAB_ADDITIONAL_STARTUP_OPTIONS",
        "TEST_ARGS",
    ]
    keyword_formatters = {"MATLAB_ADDITIONAL_STARTUP_OPTIONS": "_format_command_line"}


class MatlabAddMex(ArgumentAwareCommandInvocationDumper):
    options = ["EXECUTABLE", "MODULE", "SHARED", "R2017b", "R2018a", "EXCLUDE_FROM_ALL"]
    one_value_keywords = ["NAME", "OUTPUT_NAME", "DOCUMENTATION"]
    multi_value_keywords = ["SRC", "LINK_TO"]


class PkgCheckModules(ArgumentAwareCommandInvocationDumper):
    options = [
        "REQUIRED",
        "QUIET",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "IMPORTED_TARGET",
        "GLOBAL",
    ]


class PkgSearchModule(ArgumentAwareCommandInvocationDumper):
    options = [
        "REQUIRED",
        "QUIET",
        "NO_CMAKE_PATH",
        "NO_CMAKE_ENVIRONMENT_PATH",
        "IMPORTED_TARGET",
        "GLOBAL",
    ]


class ProtobufGenerateCpp(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["DESCRIPTORS", "EXPORT_MACRO"]


class Qt4WrapCpp(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["TARGET"]
    multi_value_keywords = ["OPTIONS"]


class Qt4WrapUi(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["OPTIONS"]


class Qt4AddResources(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["OPTIONS"]


class Qt4GenerateMoc(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["TARGET"]


class Qt4GenerateDbusInterface(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["OPTIONS"]


class Qt4CreateTranslation(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = ["OPTIONS"]


class Qt4Automoc(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["TARGET"]


class SquishAddTest(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = [
        "AUT",
        "SUITE",
        "TEST",
        "SETTINGSGROUP",
        "PRE_COMMAND",
        "POST_COMMAND",
    ]


module_command_mapping = {
    # Utility Modules
    "android_add_test_data": AndroidAddTestData,
    "check_c_source_compiles": CheckCSourceCompiles,
    "check_cxx_source_compiles": CheckCXXSourceCompiles,
    "check_fortran_source_compiles": CheckFortranSourceCompiles,
    "check_fortran_source_runs": CheckFortranSourceRuns,
    "check_include_files": CheckIncludeFiles,
    "check_ipo_supported": CheckIPOSupported,
    "check_objc_source_compiles": CheckOBJCSourceCompiles,
    "check_objcxx_source_compiles": CheckOBJCXXSourceCompiles,
    "check_pie_supported": CheckPIESupported,
    "check_struct_has_member": CheckStructHasMember,
    "check_type_size": CheckTypeSize,
    "cmake_add_fortran_subdirectory": CMakeAddFortranSubdirectory,
    "cmake_print_properties": CMakePrintProprties,
    "configure_package_config_file": ConfigurePackageConfigFile,
    "cpack_add_component": CPackAddComponent,
    "cpack_add_component_group": CPackAddComponentGroup,
    "cpack_add_install_type": CPackAddInstallType,
    "cpack_configure_downloads": CPackConfigureDownloads,
    "cpack_ifw_add_repository": CPackIFWAddRepository,
    "cpack_ifw_configure_component": CPackIFWConfigureComponent,
    "cpack_ifw_configure_component_group": CPackIFWConfigureComponentGroup,
    "cpack_ifw_update_repository": CPackIFWUpdateRepository,
    "ctest_coverage_collect_gcov": CTestCoverageCollectGCOV,
    "externalproject_add": ExternalProjectAdd,
    "externalproject_add_step": ExternalProjectAddStep,
    "feature_summary": FeatureSummary,
    "set_package_properties": SetPackageProperties,
    "fetchcontent_declare": FetchContentDeclare,
    "fetchcontent_populate": FetchContentPopulate,
    "fetchcontent_getproperties": FetchContentGetProperties,
    "find_package_handle_standard_args": FindPackageHandleStandardArgs,
    "find_package_check_version": FindPackageCheckVersion,
    "fortrancinterface_header": FortranCInterfaceHeader,
    "generate_export_header": GenerateExportHeader,
    "gtest_add_tests": GTestAddTests,
    "gtest_discover_tests": GTestDiscoverTests,
    "add_jar": AddJar,
    "install_jar": InstallJar,
    "install_jni_symlink": InstallJniSymlink,
    "install_jar_exports": InstallJarExports,
    "export_jars": ExportJars,
    "find_jar": FindJar,
    "create_javadoc": CreateJavaDoc,
    "create_javah": CreateJavah,
    "swig_add_library": SwigAddLibrary,
    "write_compiler_detection_header": WriteCompilerDetectionHeader,
    "write_basic_package_version_file": WriteBasicPackageVersionFile,
    # Find Modules
    "bison_target": BisonTarget,
    "doxygen_add_docs": DoxygenAddDocs,
    "env_module": EnvModule,
    "env_module_swap": EnvModuleSwap,
    "flex_target": FlexTarget,
    "gettext_create_translations": GettextCreateTranslations,
    "gettext_process_pot_file": GettextProcessPotFile,
    "gettext_process_po_files": GettextProcessPoFiles,
    "matlab_add_unit_test": MatlabAddUnitTest,
    "matlab_add_mex": MatlabAddMex,
    "pkg_check_modules": PkgCheckModules,
    "pkg_search_module": PkgSearchModule,
    "protobuf_generate_cpp": ProtobufGenerateCpp,
    "qt4_wrap_cpp": Qt4WrapCpp,
    "qt4_wrap_ui": Qt4WrapUi,
    "qt4_add_resources": Qt4AddResources,
    "qt4_generate_moc": Qt4GenerateMoc,
    "qt4_generate_dbus_interface": Qt4GenerateDbusInterface,
    "qt4_create_translation": Qt4CreateTranslation,
    "qt4_automoc": Qt4Automoc,
    "squish_add_test": SquishAddTest,
}
