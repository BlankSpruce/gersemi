project(ExtensionExample)

# command with specific canonical name
ExampleSpecificCanonicalName()

# command with standard properties
example_pick_movie_to_watch(
    "Search IMDB"
    GENRES
        Comedy
        Action
        Adventures
    EXCLUDE_ALREADY_WATCHED
    movie_for_tuesday
)

example_pick_movie_to_watch(
    "Ask Steve from accounting"
    GENRES
        Fantasy
    IS_FAMILY_FRIENDLY
    EXCLUDE_ALREADY_WATCHED
    YEAR_RANGE
        2017
        2022
    movie_for_sunday
)

example_pick_movie_to_watch(
    "Ask Tarantino freak"
    GENRES
        Comedy
        Western
    YEAR_RANGE
        1990
    DIRECTOR "Quentin Tarantino"
    RATING_RANGE
        3.5
        5.0
    movie_for_friday_night
)

example_pick_movie_to_watch(
    "Search in the internet"
    DIRECTOR Any
    YEAR_RANGE
        2024
        2025
    GENRES
        Comedy
        Adventure
        "Ultra specific genre that can't be summarized in a single word"
        Action
    movie_for_july_event
)

# command with sections
example_rate_movies(
    "My private spreadsheet"
    MOVIE
        "Django Unchained"
        ROUND_TO_THE_NEAREST
        RATING
            3.141592653589793238462643383279502884197169399375105820974944592307816406
    MOVIE
        "Inglorious Basterds"
        RATING 2.71828
    MOVIE
        "Pirates of the Caribbean: The Curse of the Black Pearl"
        RATING 0.57721
    MOVIE
        "Lord of the Rings: Fellowship of the Ring"
        ALTERNATIVE_TITLES "Fellowship of the Ring"
        RATING 1.618033
        ROUND_DOWN
    MOVIE
        "Leon"
        ALTERNATIVE_TITLES
            "The Professional"
            "Leon: The Professional"
            "I'm sure there is one more variant out there"
        RATING 2.41421
        ROUND_TO_THE_NEAREST
)

# command with unnamed positional arguments
example_unnamed_positional_arguments(
    front_1
    front_2
    front_3
    THINGS
        foo
        bar
        baz
        qux
    back_1
    back_2
)

# command with common keywords in standalone and in section mode
example_common_keywords_in_standalone_and_in_section(
    front_1
    front_2
    OPTION_1
    OPTION_2
    ONE_VALUE_KEYWORD_2 foo
    ONE_VALUE_KEYWORD_1 foo
    MULTI_VALUE_KEYWORD_1
        foo
        bar
        baz
    SECTION_KEYWORD
        section_front_1
        OPTION_1
        OPTION_2
        ONE_VALUE_KEYWORD_2 foo
        ONE_VALUE_KEYWORD_1 foo
        MULTI_VALUE_KEYWORD_1
            foo
            bar
            baz
        section_back_1
        section_back_2
    back_1
    back_2
    back_3
)

# command with nested sections
example_nested_sections(
    foo # level_0_arg_1
    bar # level_0_arg_2
    LEVEL_0___OPTION_1
    LEVEL_0___ONE_VALUE_KEYWORD foobar
    LEVEL_0___OPTION_2
    LEVEL_0___MULTI_VALUE_KEYWORD
        foo # level_1_arg_1
        bar # level_1_arg_2
        LEVEL_1___OPTION_1
        LEVEL_1___OPTION_2
        LEVEL_1___MULTI_VALUE_KEYWORD
            foo # level_2_arg_1
            bar # level_2_arg_2
            LEVEL_2___OPTION_3
            LEVEL_2___OPTION_1
            LEVEL_2___OPTION_2
            LEVEL_2___MULTI_VALUE_KEYWORD foo bar baz
            LEVEL_2___ONE_VALUE_KEYWORD
                foobar__________________________________________________
            LEVEL_2___MULTI_VALUE_KEYWORD
                baz
                qux
                foo__________________________________________________
            foo # level_2_arg_3
            bar # level_2_arg_4
        LEVEL_1___ONE_VALUE_KEYWORD foobar
        LEVEL_1___OPTION_3
        baz # level_1_arg_3
        qux # level_1_arg_4
    LEVEL_0___OPTION_3
    baz # level_0_arg_3
    qux # level_0_arg_4
)

# command with keyword kinds
example_add_movie_to_database(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer"
            "Cillian Murphy"
        "Kitty Oppenheimer"
            "Emily Blunt"
        "General Leslie Groves"
            "Matt Damon"
    SUMMARY
        Oppenheimer is an epic biographical thriller directed by Christopher
        Nolan.
    AVAILABLE_SUBTITLES
        English
        Spanish
)

# command with section CONFUSING_ARGUMENTS and dead "keyword_kinds" property
example_keyword_cant_be_both_section_and_special_kind(
    Frombulate
    CONFUSING_ARGUMENTS
        ARG1 foo
        ARG2 bar
)

example_keyword_cant_be_both_section_and_special_kind(
    Frombulate
    CONFUSING_ARGUMENTS
        ARG1 foo__________________________________________________
        ARG2 bar__________________________________________________
)

# command with "keyword_preprocessors" property
example_show_movie_credits(
    Oppenheimer
    ACTORS
        "Alden Ehrenreich"
        "Cillian Murphy"
        "Emily Blunt"
        "Matt Damon"
        "Robert Downey Jr."
        "Scott Grimes"
    WRITERS
        "Kai Bird"
        "Christopher Nolan"
        "Martin Sherwin"
)

# command with multiple signatures
example_compute_value(
    SUM
    sum_result
    VALUES
        1
        2
        3
        4
        5
        6
        7
        8
        9
        10
)

example_compute_value(
    PRODUCT
    product_result
    VALUES
        1.1
        2.22
        3.333
        4.4444
        5.55555
        6.666666
        7.7777777
        8.88888888
        9.999999999
)

example_compute_value(
    MAP
    map_result
    FUNCTION "square root"
    VALUES
        1
        4
        9
        16
        25
        36
        100
        10000
)

# command with dead properties
example_dead_properties(
    SOME_SIGNATURE
    THINGS
        foo
        bar
        # treated as THINGS due to no special meaning in this signature
        THIS_KEYWORD_IS_NOT_RECOGNIZED
        THAT_ONE_AS_WELL
    OPTION_KEYWORD_SIGNATURE___1
    OPTION_KEYWORD_SIGNATURE___2
)
