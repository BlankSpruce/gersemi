get_filename_component(FOO bar/filename.ext DIRECTORY)

get_filename_component(FOO bar/filename.ext NAME)

get_filename_component(FOO bar/filename.ext EXT)

get_filename_component(FOO bar/filename.ext NAME_WE)

get_filename_component(FOO bar/filename.ext LAST_EXT)

get_filename_component(FOO bar/filename.ext NAME_WLE)

get_filename_component(FOO bar/filename.ext PATH)

get_filename_component(FOO bar/filename.ext PATH CACHE)

get_filename_component(FOO bar/filename.ext BASE_DIR baz)

get_filename_component(FOO bar/filename.ext BASE_DIR baz CACHE)

get_filename_component(FOO bar/filename.ext PROGRAM)

get_filename_component(FOO bar/filename.ext PROGRAM CACHE)

get_filename_component(FOO bar/filename.ext PROGRAM PROGRAM_ARGS baz)

get_filename_component(FOO bar/filename.ext PROGRAM PROGRAM_ARGS baz CACHE)

get_filename_component(FOO bar/long_filename_______________________.ext PATH CACHE)

get_filename_component(FOO bar/long_filename_______________________.ext BASE_DIR baz CACHE)

get_filename_component(FOO bar/long_filename_______________________.ext BASE_DIR long_base_dir________________________________________________________ CACHE)

get_filename_component(FOO bar/long_filename_______________________.ext PROGRAM CACHE)

get_filename_component(FOO bar/long_filename_______________________.ext PROGRAM PROGRAM_ARGS baz CACHE)

get_filename_component(FOO bar/long_filename_______________________.ext PROGRAM PROGRAM_ARGS long_arg_var______________________________________________________ CACHE)

if(TRUE)
get_filename_component(FOO bar/filename.ext NAME)

get_filename_component(FOO bar/long_filename_______________________.ext PATH CACHE)
endif()