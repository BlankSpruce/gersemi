function(Lord_of_the_Rings_Return_of_the_King)
    cmake_parse_arguments(inner "" "" "IN_MORDOR;IN_GONDOR" ${ARGN})

    function(In_Mordor)
        set(oneValueArgs "WHAT_HAPPENS")
        set(multiValueArgs "WHO_IS_THERE")
        cmake_parse_arguments(
            _
            ""
            "${oneValueArgs}"
            "${multiValueArgs}"
            ${ARGN}
        )
    endfunction()

    macro(In_Gondor)
        set(oneValueArgs "WHAT_HAPPENS")
        set(multiValueArgs "WHO_IS_THERE")
        cmake_parse_arguments(
            _
            ""
            "${oneValueArgs}"
            "${multiValueArgs}"
            ${ARGN}
        )
    endmacro()

    block()
        function(In_Shire)
            set(oneValueArgs "WHAT_HAPPENS")
            set(multiValueArgs "WHO_IS_THERE")
            cmake_parse_arguments(
                _
                ""
                "${oneValueArgs}"
                "${multiValueArgs}"
                ${ARGN}
            )
        endfunction()
    endblock()

    In_Mordor(
        WHAT_HAPPENS "Getting closer to Mount Doom"
        WHO_IS_THERE ${inner_IN_MORDOR}
    )

    In_Gondor(
        WHAT_HAPPENS
            "Preparations for the grand battle next to the Black Gate to pull Sauron's attention"
        WHO_IS_THERE ${inner_IN_GONDOR}
    )

    In_Shire(
        WHAT_HAPPENS "Saruman takes control"
        WHO_IS_THERE #
            Saruman
            "Grima Wormtongue"
    )
endfunction()

Lord_of_the_Rings_Return_of_the_King(
    IN_MORDOR Frodo Sam
    IN_GONDOR
        Merry
        Pippin
        Aragorn
        Gimli
        Legolas
        Gandalf
)
