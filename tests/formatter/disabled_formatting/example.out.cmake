the_hobbit(
    BURGLAR "Bilbo Baggins"
    WIZARD Gandalf
    DWARVES
        "Thorin Oakenshield"
        Fili
        Kili
        Balin
        Dwalin
        Oin
        Gloin
        Dori
        Nori
        Ori
        Bifur
        Bofur
        Bombur
)

# gersemi: off
the_fellowship_of_the_ring     (
    RING_BEARER Frodo GARDENER Samwise
    Merry Pippin Aragon
            Boromir
            Gimli
       Legolas
       Gandalf
       )
# gersemi: on

# gersemi: off
the_two_towers(
            RING_BEARER Frodo
        GARDENER Samwise
    Merry Pippin Aragon
    # gersemi: on
    Boromir
    Gimli
    Legolas
    Gandalf
)

# gersemi: off
function(how_to_make_a_successful_movie args)
step_one_have_a_good_scenario()
    # gersemi: on
    step_two_make_the_movie()
endfunction()
