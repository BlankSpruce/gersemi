ctest_upload(FILES FOO QUIET CAPTURE_CMAKE_ERROR BAR)

ctest_upload(FILES FOO BAR BAZ FOO BAR BAZ FOO BAR BAZ QUIET CAPTURE_CMAKE_ERROR BAR)

ctest_upload(FILES long_arg____________________________________________________________ QUIET CAPTURE_CMAKE_ERROR long_arg____________________________________________________________)

ctest_upload(FILES long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ long_arg____________________________________________________________ QUIET CAPTURE_CMAKE_ERROR long_arg____________________________________________________________)