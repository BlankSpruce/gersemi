file(READ foo bar OFFSET 0 LIMIT 100 HEX)

file(READ long_filename__________________________ long_variable_name_________________________ OFFSET 0 LIMIT 100 HEX)

file(STRINGS foo bar LENGTH_MAXIMUM 100)

file(STRINGS foo bar LENGTH_MAXIMUM 100 LENGTH_MINIMUM 100 LIMIT_COUNT 100 LIMIT_OUTPUT 100 NEWLINE_CONSUME NO_HEX_CONVERSION REGEX regex ENCODING UTF-8)

file(STRINGS long_filename__________________________ long_variable_name_________________________ LENGTH_MAXIMUM 100)

file(STRINGS long_filename__________________________ long_variable_name_________________________ LENGTH_MAXIMUM 100 LENGTH_MINIMUM 100 LIMIT_COUNT 100 LIMIT_OUTPUT 100 NEWLINE_CONSUME NO_HEX_CONVERSION REGEX regex ENCODING UTF-8)

file(MD5 foo bar)

file(MD5 long_filename__________________________ long_variable_name_________________________)

file(TIMESTAMP foo bar format UTC)

file(TIMESTAMP long_filename__________________________ long_variable_name_________________________ long_format_________________________ UTC)

file(GET_RUNTIME_DEPENDENCIES  RESOLVED_DEPENDENCIES_VAR foo)

file(GET_RUNTIME_DEPENDENCIES  RESOLVED_DEPENDENCIES_VAR foo  UNRESOLVED_DEPENDENCIES_VAR foo
  CONFLICTING_DEPENDENCIES_PREFIX foo  EXECUTABLES foo bar  LIBRARIES foo bar  MODULES foo bar
  DIRECTORIES foo bar  BUNDLE_EXECUTABLE foo  PRE_INCLUDE_REGEXES foo bar  PRE_EXCLUDE_REGEXES foo bar
  POST_INCLUDE_REGEXES foo bar  POST_EXCLUDE_REGEXES foo bar
)

file(WRITE foo bar)

file(WRITE long_filename__________________________ long_content________________________________________________)

file(APPEND foo bar)

file(APPEND long_filename__________________________ long_content________________________________________________)

file(TOUCH foo bar)

file(TOUCH long_filename__________________________ long_filename__________________________)

file(TOUCH_NOCREATE foo bar)

file(TOUCH_NOCREATE long_filename__________________________ long_filename__________________________)

file(GENERATE OUTPUT foo INPUT bar CONDITION baz)

file(GENERATE OUTPUT foo CONTENT bar CONDITION baz)

file(GENERATE OUTPUT long_filename__________________________  INPUT long_filename__________________________  CONDITION long_condition__________________________ )

file(GLOB foo LIST_DIRECTORIES true RELATIVE bar CONFIGURE_DEPENDS glob)

file(GLOB long_variable_name_________________________ LIST_DIRECTORIES true RELATIVE bar CONFIGURE_DEPENDS long_glob_________________________)

file(GLOB_RECURSE foo LIST_DIRECTORIES true RELATIVE bar CONFIGURE_DEPENDS glob)

file(GLOB_RECURSE long_variable_name_________________________ LIST_DIRECTORIES true RELATIVE bar CONFIGURE_DEPENDS long_glob_________________________)

file(REMOVE foo bar)

file(REMOVE long_filename__________________________ long_filename__________________________)

file(REMOVE_RECURSE foo bar)

file(REMOVE_RECURSE long_filename__________________________ long_filename__________________________)

file(MAKE_DIRECTORY foo bar RESULT result)

file(MAKE_DIRECTORY long_filename__________________________ long_filename__________________________ RESULT result)

file(COPY foo bar DESTINATION baz)

file(COPY foo bar DESTINATION baz FILE_PERMISSIONS qux DIRECTORY_PERMISSIONS qux NO_SOURCE_PERMISSIONS USE_SOURCE_PERMISSIONS FOLLOW_SYMLINK_CHAIN FILES_MATCHING PATTERN pattern REGEX regex EXCLUDE PERMISSIONS foo bar baz)

file(INSTALL foo bar DESTINATION baz)

file(INSTALL foo bar DESTINATION baz FILE_PERMISSIONS qux DIRECTORY_PERMISSIONS qux NO_SOURCE_PERMISSIONS USE_SOURCE_PERMISSIONS FOLLOW_SYMLINK_CHAIN FILES_MATCHING PATTERN pattern REGEX regex EXCLUDE PERMISSIONS foo bar baz)

file(SIZE foo bar)

file(SIZE long_filename__________________________ long_filename__________________________)

file(READ_SYMLINK foo bar)

file(READ_SYMLINK long_filename__________________________ long_filename__________________________)

file(CREATE_LINK foo bar)

file(CREATE_LINK foo bar RESULT result COPY_ON_ERROR SYMBOLIC)

file(CREATE_LINK long_filename__________________________ long_filename__________________________ RESULT result COPY_ON_ERROR SYMBOLIC)

file(RELATIVE_PATH foo bar baz)

file(RELATIVE_PATH long_filename__________________________ long_filename__________________________ long_filename__________________________)

file(TO_CMAKE_PATH foo bar)

file(TO_CMAKE_PATH long_filename__________________________ long_filename__________________________)

file(TO_NATIVE_PATH foo bar)

file(TO_NATIVE_PATH long_filename__________________________ long_filename__________________________)

file(DOWNLOAD url file)

file(DOWNLOAD url file INACTIVITY_TIMEOUT 100 LOG foo SHOW_PROGRESS STATUS bar TIMEOUT 100 USERPWD root:root HTTPHEADER header NETRC REQUIRED NETRC_FILE foo EXPECTED_HASH ALGO=bar EXPECTED_MD5 md5 TLS_VERIFY ON TLS_CAINFO baz)

file(UPLOAD url file)

file(UPLOAD url file INACTIVITY_TIMEOUT 100 LOG foo SHOW_PROGRESS STATUS bar TIMEOUT 100 USERPWD root:root HTTPHEADER header NETRC REQUIRED NETRC_FILE foo)

file(LOCK foo)

file(LOCK foo DIRECTORY RELEASE GUARD FUNCTION RESULT_VARIABLE bar TIMEOUT 100)

file(LOCK long_filename__________________________ DIRECTORY RELEASE GUARD FUNCTION RESULT_VARIABLE long_variable_name__________________________ TIMEOUT 100)

file(#[[some bracket comment]] LOCK foo DIRECTORY RELEASE GUARD FUNCTION RESULT_VARIABLE bar TIMEOUT 100)

file(# some line comment
LOCK foo DIRECTORY RELEASE GUARD FUNCTION RESULT_VARIABLE bar TIMEOUT 100)