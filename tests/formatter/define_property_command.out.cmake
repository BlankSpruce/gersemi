define_property(GLOBAL PROPERTY FOO)

define_property(DIRECTORY PROPERTY FOO INHERITED)

define_property(TARGET PROPERTY FOO BRIEF_DOCS BAR)

define_property(SOURCE PROPERTY FOO FULL_DOCS BAR)

define_property(TEST PROPERTY FOO INHERITED BRIEF_DOCS BAR FULL_DOCS BAZ)

define_property(
    VARIABLE
    PROPERTY FOO
    BRIEF_DOCS BAR BAZ FOO
    FULL_DOCS FOO BAR BAZ
)

define_property(
    CACHED_VARIABLE
    PROPERTY FOO
    INHERITED
    BRIEF_DOCS BAR BAZ FOO
    FULL_DOCS FOO BAR BAZ
)

define_property(
    GLOBAL
    PROPERTY
        long_arg____________________________________________________________
)

define_property(
    DIRECTORY
    PROPERTY
        long_arg____________________________________________________________
    INHERITED
)

define_property(
    TARGET
    PROPERTY
        long_arg____________________________________________________________
    BRIEF_DOCS
        long_arg____________________________________________________________
)

define_property(
    SOURCE
    PROPERTY
        long_arg____________________________________________________________
    FULL_DOCS
        long_arg____________________________________________________________
)

define_property(
    TEST
    PROPERTY
        long_arg____________________________________________________________
    INHERITED
    BRIEF_DOCS
        long_arg____________________________________________________________
    FULL_DOCS
        long_arg____________________________________________________________
)

define_property(
    VARIABLE
    PROPERTY
        long_arg____________________________________________________________
    BRIEF_DOCS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    FULL_DOCS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

define_property(
    CACHED_VARIABLE
    PROPERTY
        long_arg____________________________________________________________
    INHERITED
    BRIEF_DOCS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    FULL_DOCS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)
