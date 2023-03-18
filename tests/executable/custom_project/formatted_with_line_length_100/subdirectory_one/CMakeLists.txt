function(
    the_fellowship_of_the_ring
    some
    unnamed
    not
    keyworded
    arguments
)
    set(option_keywords FRODO SAM MERRY PIPPIN)
    set(one_value_keywords ARAGORN BOROMIR GIMLI LEGOLAS)
    set(multi_value_keywords GANDALF_THE_GREY)
    cmake_parse_arguments(
        the_fellowship_of_the_ring_prefix
        "${option_keywords}"
        "${one_value_keywords}"
        "${multi_value_keywords}"
        ${ARGN}
    )
endfunction()

# In Shire starts the journey
the_fellowship_of_the_ring(FRODO SAM)

# shortly after join Merry and Pippin
the_fellowship_of_the_ring(FRODO SAM MERRY PIPPIN)

# in Bree they are joined by Aragorn
the_fellowship_of_the_ring(FRODO SAM MERRY PIPPIN ARAGORN who_is_also_known_as_Strider)

# after they arrive in Rivendell the Fellowship is formed
the_fellowship_of_the_ring(
    FRODO
    SAM
    MERRY
    PIPPIN
    ARAGORN you_have_my_sword
    LEGOLAS and_you_have_my_bow
    GIMLI "and my axe"
    BOROMIR [[...then Gondor will see it done]]
    GANDALF_THE_GREY is wise and silent
)

# in Moria they depart with Gandalf
the_fellowship_of_the_ring(
    FRODO
    SAM
    MERRY
    PIPPIN
    ARAGORN you_have_my_sword
    LEGOLAS and_you_have_my_bow
    GIMLI "and my axe"
    BOROMIR [[...then Gondor will see it done]]
)

# at falls of Rauros they are ambushed and then later split
the_fellowship_of_the_ring(FRODO SAM)
the_fellowship_of_the_ring(MERRY PIPPIN)
the_fellowship_of_the_ring(ARAGORN you_have_my_sword LEGOLAS and_you_have_my_bow GIMLI "and my axe")

macro(the_two_towers some arguments)
    set(going_to_mordor FRODO SAM GOLLUM)
    set(taken_to_isengard MERRY PIPPIN)
    set(looking_for_hobbits ARAGORN GIMLI LEGOLAS GANDALF_THE_WHITE)
    cmake_parse_arguments(
        the_two_towers_prefix
        "${going_to_mordor}"
        "${taken_to_isengard}"
        "${looking_for_hobbits}"
        ${ARGN}
    )
endmacro()

# reunion in Fangorn
the_two_towers(
    ARAGORN you have my sword
    LEGOLAS and you have my bow
    GIMLI and my axe
    GANDALF_THE_WHITE more powerful
)

# in Edoras
the_two_towers(
    ARAGORN you_have_my_sword
    LEGOLAS and_you_have_my_bow
    GIMLI "and my axe"
    GANDALF_THE_WHITE
        "Theoden, son of Thengel"
        "I have returend and I bring warning and wise counsel"
        "A storm is brewing"
        "All good people must stand together or be destroyed"
)

# reunion in Isengard
the_two_towers(
    MERRY welcome_to
    PIPPIN "Isengard"
    ARAGORN you_have_my_sword
    LEGOLAS and_you_have_my_bow
    GIMLI "and my axe"
    GANDALF_THE_WHITE more powerful
)

# going to Mordor
the_two_towers(FRODO SAM GOLLUM)

function(
    the_return_of_the_king
    some
    unnamed
    not
    keyworded
    arguments
)
    set(in_mordor FRODO SAM GOLLUM)
    set(the_king ARAGORN)
    set(helping_the_king
        MERRY
        PIPPIN
        GIMLI
        LEGOLAS
        GANDALF_THE_WHITE
    )
    cmake_parse_arguments(
        the_return_of_the_king_prefix
        "${in_mordor}"
        "${the_king}"
        "${helping_the_king}"
        ${ARGN}
    )
endfunction()

if(TRUE)
    # at Mount Doom
    the_return_of_the_king(FRODO SAM GOLLUM)

    # eagles are coming
    the_return_of_the_king(
        FRODO
        SAM
        GOLLUM
        ARAGORN "For Frodo"
        PIPPIN "eagles are coming"
        MERRY [[fighting]]
        GANDALF_THE_WHITE [[also fighthing]]
        GIMLI "Never thought" "I'd die fighting side by side" "with an Elf"
        LEGOLAS "What about side by side" "with a friend?"
    )

    # reunion in Minas Tirith
    the_return_of_the_king(
        FRODO
        SAM
        MERRY
        PIPPIN
        ARAGORN the_king
        LEGOLAS ""
        GIMLI ""
        GANDALF_THE_WHITE ""
    )
endif()
