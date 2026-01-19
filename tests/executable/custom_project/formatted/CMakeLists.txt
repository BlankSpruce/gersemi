project(FOO)

include(back_to_the_future)
include(back_to_the_future_sequels)

add_library(foo INTERFACE)
add_library(bar INTERFACE)

add_executable(baz)

back_to_the_future(
    foo
    DELOREAN
    FLUX_CAPACITOR 1.21gigawatts
    MARTY_MCFLY one two three four
    EMMETT_BROWN One Two Three Four
)

back_to_the_future_part_ii(
    foo
    bar
    BIFF_TANNEN looking for almanach
    OLDER_MARTY_MCFLY fired
    YOUNGER_MARTY_MCFLY surprised
    EMMETT_DOC_BROWN
        "one two three four five"
        "six seven eight nine ten eleven twelve"
)

back_to_the_future_part_iii(
    baz
    foo
    bar
    MAD_DOG
    DOC_BROWN "trapped in 1885"
    DELOREAN "pushed by locomotive"
    MARTY "returns to 1985 without Doc"
    CLARA_CLAYTON
        one
        two
        three__________________________________________________
        four
    FLUX_CAPACITOR
        "attached to flying steam locomotive manned by Doc who took Clara"
        "and their children for a time travel ride"
)

add_subdirectory(subdirectory_one)
add_subdirectory(subdirectory_two)
