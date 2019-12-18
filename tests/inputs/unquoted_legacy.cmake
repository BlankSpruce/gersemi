foo(
    SomeUnquotedArgument
    another_unquoted_argument
    ${some_referenced_variable}
    -unquoted_legacy="argument1 argument2"
    ${yet_another_unquoted}="${${legacy_argument}}"
    )
