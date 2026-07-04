set(MY_SOURCES #[[plain bracket comment]] c.h a.h d_____________________________________________.h c.h a.h b.h CACHE INTERNAL "Short docstring" FORCE)

set(MY_SOURCES #[[gersemi: sort+unique]] c.h a.h d_____________________________________________.h c.h a.h b.h CACHE INTERNAL "Short docstring" FORCE)

set(MY_SOURCES #[[gersemi: sort]] c.h a.h d_____________________________________________.h c.h a.h b.h CACHE INTERNAL "Short docstring" FORCE)

set(MY_SOURCES #[[gersemi: unique]] c.h a.h d_____________________________________________.h c.h a.h b.h CACHE INTERNAL "Short docstring" FORCE)

set(OppenheimerCast #[[gersemi: pairs]] "J. Robert Oppenheimer" "Cillian Murphy" "Kitty Oppenheimer" "Emily Blunt" "General Leslie Groves" "Matt Damon")

set(add_custom_command_COMMAND #[[gersemi: command_line]] clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml)

set(add_custom_command_COMMAND_2 #[[gersemi: command_line]]
clang-format #
-length=1000 #
-sort-includes #
-style=some_kind_of_style #
-verbose #
-output-replacements-xml
)

set(multiple_phantom_comments #[[gersemi: sort+unique]] c.h a.h d_____________________________________________.h c.h a.h b.h #[[gersemi: pairs]] "J. Robert Oppenheimer" "Cillian Murphy" "Kitty Oppenheimer" "Emily Blunt" "General Leslie Groves" "Matt Damon" #[[gersemi: command_line]]
clang-format #
-length=1000 #
-sort-includes #
-style=some_kind_of_style #
-verbose #
-output-replacements-xml CACHE INTERNAL "Short docstring" FORCE)

set(commented_phantom_keyword #[[gersemi: sort+unique]] # my line comment
c.h a.h d_____________________________________________.h c.h a.h b.h #[[gersemi: pairs]] #[[my bracket comment]] "J. Robert Oppenheimer" "Cillian Murphy" "Kitty Oppenheimer" "Emily Blunt" "General Leslie Groves" "Matt Damon" CACHE INTERNAL "Short docstring" FORCE)

set(raw_phantom_keyword_just_indents #[[gersemi: raw]] c.h a.h d_____________________________________________.h c.h a.h b.h CACHE INTERNAL "Short docstring" FORCE)

set(install_args #[[gersemi: as_command=install]] TARGETS long_arg____________________________________________________________ EXPORT long_arg____________________________________________________________ PUBLIC_HEADER DESTINATION long_arg____________________________________________________________ PERMISSIONS OWNER_READ CONFIGURATIONS Debug COMPONENT long_arg____________________________________________________________ NAMELINK_COMPONENT long_arg____________________________________________________________ OPTIONAL EXCLUDE_FROM_ALL NAMELINK_ONLY INCLUDES DESTINATION long_arg____________________________________________________________)
