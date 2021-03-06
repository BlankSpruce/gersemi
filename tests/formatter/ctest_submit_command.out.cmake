ctest_submit(PARTS Start FILES FOO SUBMIT_URL BAR BUILD_ID BAZ HTTPHEADER FOO)

ctest_submit(
    PARTS Start
    FILES FOO
    SUBMIT_URL BAR
    BUILD_ID BAZ
    HTTPHEADER FOO
    RETRY_COUNT BAR
    RETRY_DELAY BAZ
    RETURN_VALUE FOO
    CAPTURE_CMAKE_ERROR BAR
    QUIET
)

ctest_submit(
    PARTS Start
    FILES FOO BAR BAZ
    SUBMIT_URL BAR
    BUILD_ID BAZ
    HTTPHEADER FOO
    RETRY_COUNT BAR
    RETRY_DELAY BAZ
    RETURN_VALUE FOO
    CAPTURE_CMAKE_ERROR BAR
    QUIET
)

ctest_submit(
    PARTS
        Start
        Update
        Configure
        Build
        Test
        Coverage
        MemCheck
        Notes
        ExtraFiles
        Upload
        Submit
        Done
    FILES FOO
    SUBMIT_URL BAR
    BUILD_ID BAZ
    HTTPHEADER FOO
    RETRY_COUNT BAR
    RETRY_DELAY BAZ
    RETURN_VALUE FOO
    CAPTURE_CMAKE_ERROR BAR
    QUIET
)

ctest_submit(
    PARTS
        Start
        Update
        Configure
        Build
        Test
        Coverage
        MemCheck
        Notes
        ExtraFiles
        Upload
        Submit
        Done
    FILES FOO BAR BAZ
    SUBMIT_URL BAR
    BUILD_ID BAZ
    HTTPHEADER FOO
    RETRY_COUNT BAR
    RETRY_DELAY BAZ
    RETURN_VALUE FOO
    CAPTURE_CMAKE_ERROR BAR
    QUIET
)

ctest_submit(
    PARTS Start
    FILES long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
    BUILD_ID
        long_arg____________________________________________________________
    HTTPHEADER
        long_arg____________________________________________________________
)

ctest_submit(
    PARTS Start
    FILES long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
    BUILD_ID
        long_arg____________________________________________________________
    HTTPHEADER
        long_arg____________________________________________________________
    RETRY_COUNT
        long_arg____________________________________________________________
    RETRY_DELAY
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
    QUIET
)

ctest_submit(
    PARTS Start
    FILES
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
    BUILD_ID
        long_arg____________________________________________________________
    HTTPHEADER
        long_arg____________________________________________________________
    RETRY_COUNT
        long_arg____________________________________________________________
    RETRY_DELAY
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
    QUIET
)

ctest_submit(
    PARTS
        Start
        Update
        Configure
        Build
        Test
        Coverage
        MemCheck
        Notes
        ExtraFiles
        Upload
        Submit
        Done
    FILES long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
    BUILD_ID
        long_arg____________________________________________________________
    HTTPHEADER
        long_arg____________________________________________________________
    RETRY_COUNT
        long_arg____________________________________________________________
    RETRY_DELAY
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
    QUIET
)

ctest_submit(
    PARTS
        Start
        Update
        Configure
        Build
        Test
        Coverage
        MemCheck
        Notes
        ExtraFiles
        Upload
        Submit
        Done
    FILES
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
    BUILD_ID
        long_arg____________________________________________________________
    HTTPHEADER
        long_arg____________________________________________________________
    RETRY_COUNT
        long_arg____________________________________________________________
    RETRY_DELAY
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
    QUIET
)

ctest_submit(CDASH_UPLOAD FOO CDASH_UPLOAD_TYPE BAR SUBMIT_URL BAZ)

ctest_submit(
    CDASH_UPLOAD FOO
    CDASH_UPLOAD_TYPE BAR
    SUBMIT_URL BAZ
    HTTPHEADER FOO
    RETRY_COUNT BAR
    RETRY_DELAY BAZ
    RETURN_VALUE FOO
    QUIET
)

ctest_submit(
    CDASH_UPLOAD
        long_arg____________________________________________________________
    CDASH_UPLOAD_TYPE
        long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
)

ctest_submit(
    CDASH_UPLOAD
        long_arg____________________________________________________________
    CDASH_UPLOAD_TYPE
        long_arg____________________________________________________________
    SUBMIT_URL
        long_arg____________________________________________________________
    HTTPHEADER
        long_arg____________________________________________________________
    RETRY_COUNT
        long_arg____________________________________________________________
    RETRY_DELAY
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    QUIET
)
