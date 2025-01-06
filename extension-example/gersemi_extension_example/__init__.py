"""
Extension module has to follow the naming convention gersemi_{module_name} like
gersemi_example_module, gersemi_acme_corporation, gersemi_qt etc.
"""

command_definitions = {
    #
    # Key defines canonical name. Usually builtin CMake commands are formatted
    # with lower case. Among exception to this rule there are commands from
    # ExternalProject module like ExternalProject_Add.
    #
    # In this example any variant of ExampleSpecificCanonicalName like:
    # - examplespecificcanonicalname
    # - EXAMPLESPECIFICCANONICALNAME
    # - eXaMpLeSpEcIfIcCaNoNiCaLnAmE
    # will be reformatted to ExampleSpecificCanonicalName.
    #
    "ExampleSpecificCanonicalName": {},
    #
    # In the simplest case commands can have one signature and such signature
    # will have the following properties:
    # 1) Front positional arguments: these are arguments appearing at the front
    # of command invocation that aren't attached to any keyword.
    # Example from builtin CMake commands:
    #
    #     configure_file(<input> <output> ...)
    #
    # 2) Back positional arguments: these are arguments appearing at the back
    # of command invocation that aren't attached to any keyword.
    # Example:
    #
    #     get_source_file_property(... <property>)
    #
    # 3) Options: these are arguments that don't have any value following them.
    # Example:
    #
    #     include(... [OPTIONAL] [NO_POLICY_SCOPE] ...)
    #
    # 4) One value keywords: these are arguments that have one value following
    # them. Example:
    #
    #     add_test(NAME <name> ... [WORKING_DIRECTORY <dir>] ...)
    #
    # 5) Multi value keywords: these are arguments that have at least one value
    # following them. Example:
    #
    #     target_include_directories(
    #         ...
    #         <INTERFACE|PUBLIC|PRIVATE> [items1...]
    #         [<INTERFACE|PUBLIC|PRIVATE> [items2...]]
    #         ...
    #     )
    #
    "example_pick_movie_to_watch": {
        "front_positional_arguments": ["how_to_pick_movie"],
        "options": ["EXCLUDE_ALREADY_WATCHED", "IS_FAMILY_FRIENDLY"],
        "one_value_keywords": ["DIRECTOR"],
        "multi_value_keywords": ["GENRES", "YEAR_RANGE", "RATING_RANGE"],
        "back_positional_arguments": ["output_variable"],
    },
    #
    # Names of positional arguments aren't used so they can represented as empty
    # strings or gibberish names as long as number of these arguments correctly
    # model the command. For documentation purposes it's better to name these
    # arguments though.
    #
    "example_unnamed_positional_arguments": {
        "front_positional_arguments": ["", "lorem-ipsum-dolor-sit-amet", ""],
        "multi_value_keywords": ["THINGS"],
        "back_positional_arguments": ["", ""],
    },
    #
    # 6) Multi value keywords can form sections with their own positional
    # arguments and keywords. Example from CMake builtins:
    #
    #     export(
    #         SETUP <export-name>
    #         [PACKAGE_DEPENDENCY
    #              <dep>
    #             [ENABLED (<bool-true>|<bool-false>|AUTO)]
    #             [EXTRA_ARGS <args>...]
    #         ] [...]
    #         [TARGET
    #             <target>
    #             [XCFRAMEWORK_LOCATION <location>]
    #         ] [...]
    #     )
    #
    "example_rate_movies": {
        "front_positional_arguments": ["database"],
        "options": ["RATE_IN_ONE_TRANSACTION"],
        "multi_value_keywords": ["MOVIE"],
        #
        # Each multi value keyword defined in "sections" can be customized
        # in the same way as base case presented in example_pick_movie_to_watch.
        #
        "sections": {
            "MOVIE": {
                "front_positional_arguments": ["original_title"],
                "options": ["ROUND_UP", "ROUND_DOWN", "ROUND_TO_THE_NEAREST"],
                "one_value_keywords": ["RATING"],
                "multi_value_keywords": ["ALTERNATIVE_TITLES"],
            }
        },
    },
    #
    # Nested sections are supported but perhaps it's better to avoid designing
    # such commands.
    #
    "example_nested_sections": {
        "front_positional_arguments": ["level_0_arg_1", "level_0_arg_2"],
        "back_positional_arguments": ["level_0_arg_3", "level_0_arg_4"],
        "options": [
            "LEVEL_0___OPTION_1",
            "LEVEL_0___OPTION_2",
            "LEVEL_0___OPTION_3",
        ],
        "one_value_keywords": ["LEVEL_0___ONE_VALUE_KEYWORD"],
        "multi_value_keywords": ["LEVEL_0___MULTI_VALUE_KEYWORD"],
        "sections": {
            "LEVEL_0___MULTI_VALUE_KEYWORD": {
                "front_positional_arguments": [
                    "level_1_arg_1",
                    "level_1_arg_2",
                ],
                "back_positional_arguments": [
                    "level_1_arg_3",
                    "level_1_arg_4",
                ],
                "options": [
                    "LEVEL_1___OPTION_1",
                    "LEVEL_1___OPTION_2",
                    "LEVEL_1___OPTION_3",
                ],
                "one_value_keywords": ["LEVEL_1___ONE_VALUE_KEYWORD"],
                "multi_value_keywords": ["LEVEL_1___MULTI_VALUE_KEYWORD"],
                "sections": {
                    "LEVEL_1___MULTI_VALUE_KEYWORD": {
                        "front_positional_arguments": [
                            "level_2_arg_1",
                            "level_2_arg_2",
                        ],
                        "back_positional_arguments": [
                            "level_2_arg_3",
                            "level_2_arg_4",
                        ],
                        "options": [
                            "LEVEL_2___OPTION_1",
                            "LEVEL_2___OPTION_2",
                            "LEVEL_2___OPTION_3",
                        ],
                        "one_value_keywords": ["LEVEL_2___ONE_VALUE_KEYWORD"],
                        "multi_value_keywords": ["LEVEL_2___MULTI_VALUE_KEYWORD"],
                    }
                },
            }
        },
    },
    #
    # 7) Another kind of specialized formatting available for multi value
    # keywords is specifying "keyword_kinds" entry. Available kinds:
    # - "pairs": values after the keyword will be grouped into pairs
    # Example (PROPERTIES keyword):
    #
    #     set_directory_properties(
    #         PROPERTIES
    #             <prop1> <value1>
    #             [<prop2> <value2>]
    #             ...
    #     )
    #
    # - "command_line": values after the keyword are treated like a sequence of
    # words in command line and will flow to the next line once line length
    # limit is reached.
    # Example (COMMAND keyword):
    #
    #     execute_process(
    #         COMMAND <cmd1> [<arguments>]
    #         [COMMAND <cmd2> [<arguments>]]...
    #         ...
    #     )
    #
    "example_add_movie_to_database": {
        "front_positional_arguments": ["movie-name"],
        "one_value_keywords": ["DIRECTOR"],
        "multi_value_keywords": ["AVAILABLE_SUBTITLES", "CAST", "SUMMARY"],
        "keyword_kinds": {
            "CAST": "pairs",
            "SUMMARY": "command_line",
        },
    },
    #
    # 8) Finally command can have multiple signatures which are selected
    # through value of first argument. Example:
    #
    #     install(TARGETS <target>... [...])
    #     install(IMPORTED_RUNTIME_ARTIFACTS <target>... [...])
    #     install({FILES | PROGRAMS} <file>... [...])
    #     install(DIRECTORY <dir>... [...])
    #     install(SCRIPT <file> [...])
    #     install(CODE <code> [...])
    #     install(EXPORT <export-name> [...])
    #     install(PACKAGE_INFO <package-name> [...])
    #     install(RUNTIME_DEPENDENCY_SET <set-name> [...])
    #
    # Signatures are specified through "signatures" entries
    # and each signature can specify the same properties as in base case.
    #
    "example_compute_value": {
        "signatures": {
            "SUM": {
                "front_positional_arguments": ["result-variable"],
                "multi_value_keywords": ["VALUES"],
            },
            "PRODUCT": {
                "front_positional_arguments": ["result-variable"],
                "multi_value_keywords": ["VALUES"],
            },
            "MAP": {
                "front_positional_arguments": ["result-variable"],
                "one_value_keywords": ["FUNCTION"],
                "multi_value_keywords": ["VALUES"],
            },
        }
    },
    #
    # Since "signatures" property takes precedence over base case properties
    # one should avoid specifying other properties.
    #
    "example_dead_properties": {
        "signatures": {
            "SOME_SIGNATURE": {
                "options": [
                    "OPTION_KEYWORD_SIGNATURE___1",
                    "OPTION_KEYWORD_SIGNATURE___2",
                ],
                "multi_value_keywords": ["THINGS"],
            },
        },
        "options": ["THIS_KEYWORD_IS_NOT_RECOGNIZED", "THAT_ONE_AS_WELL"],
    },
}
