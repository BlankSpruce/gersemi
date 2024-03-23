cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
project(example CXX)

message(STATUS "This is example project")
message(
	STATUS
	"Here is yet another but much much longer message that should be displayed"
)

# project version
set(VERSION_MAJOR 0)
set(VERSION_MINOR 1)
set(VERSION_PATCH 0)

add_compile_options(
	-Wall
	-Wpedantic
	-fsanitize=address
	-fconcepts
	-fsomething-else
)

if(NOT ${SOME_OPTION})
	add_compile_options(-Werror)
endif()

# foobar library
add_library(foobar)
add_library(example::foobar ALIAS foobar)

target_sources(
	foobar
	PUBLIC
		include/some_subdirectory/header.hpp
		include/another_subdirectory/header.hpp
	PRIVATE
		src/some_subdirectory/src1.cpp
		src/some_subdirectory/src1.cpp
		src/another_subdirectory/src1.cpp
		src/another_subdirectory/src2.cpp
		src/another_subdirectory/src3.cpp
)

target_include_directories(
	foobar
	INTERFACE
		$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
		$<INSTALL_INTERFACE:include>
)

target_link_libraries(
	foobar
	PUBLIC example::dependency_one example::dependency_two
	PRIVATE
		example::some_util
		external::some_lib
		external::another_lib
		Boost::Boost
)

include(GNUInstallDirs)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})

# example executable
add_executable(app main.cpp)
target_link_libraries(app PRIVATE example::foobar Boost::Boost)

# tests
include(CTest)
include(GTest)
enable_testing()
add_subdirectory(tests)

# some helper function - see more details in "Let's make a deal" section
function(add_test_executable)
	set(
		OPTIONS
		QUIET
		VERBOSE
		SOME_PARTICULARLY_LONG_KEYWORD_THAT_ENABLES_SOMETHING
	)
	set(ONE_VALUE_ARGS NAME TESTED_TARGET)
	set(MULTI_VALUE_ARGS SOURCES DEPENDENCIES)

	cmake_parse_arguments(
		THIS_FUNCTION_PREFIX
		${OPTIONS}
		${ONE_VALUE_ARGS}
		${MULTI_VALUE_ARGS}
	)
	# rest of the function
endfunction()

add_test_executable(
	NAME foobar_tests
	TESTED_TARGET foobar
	SOURCES
		some_test1.cpp
		some_test2.cpp
		some_test3.cpp
		some_test4.cpp
		some_test5.cpp
	QUIET
	DEPENDENCIES googletest::googletest
)

add_custom_command(
	OUTPUT ${SOMETHING_TO_OUTPUT}
	COMMAND ${CMAKE_COMMAND} -E cat foobar
	COMMAND cmake -E echo foobar
	COMMAND
		cmake -E echo "something quite a bit                             longer"
	WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/something
	DEPENDS
		${CMAKE_CURRENT_SOURCE_DIR}/something
		${CMAKE_CURRENT_SOURCE_DIR}/something_else
	COMMENT "example custom command"
)
