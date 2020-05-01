project(FOO)

project(FOO CXX FORTRAN)

project(FOO CXX FORTRAN FOO BAR BAZ)

project(long_arg____________________________________________________________)

project(
    long_arg____________________________________________________________
    CXX
    FORTRAN
)

project(
    long_arg____________________________________________________________
    CXX
    FORTRAN
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

project(FOO VERSION 1)

project(FOO VERSION 1.2 DESCRIPTION BAR)

project(FOO VERSION 1.2.3 DESCRIPTION BAR HOMEPAGE_URL BAZ)

project(FOO VERSION 1.2.3.4 DESCRIPTION BAR HOMEPAGE_URL BAZ LANGUAGES QUX FOO)

project(
    FOO
    VERSION 1.2.3.4
    DESCRIPTION BAR
    HOMEPAGE_URL BAZ
    LANGUAGES QUX FOO BAR BAZ
)

project(
    long_arg____________________________________________________________
    VERSION 1
)

project(
    long_arg____________________________________________________________
    VERSION 1.2
    DESCRIPTION
        long_arg____________________________________________________________
)

project(
    long_arg____________________________________________________________
    VERSION 1.2.3
    DESCRIPTION
        long_arg____________________________________________________________
    HOMEPAGE_URL
        long_arg____________________________________________________________
)

project(
    long_arg____________________________________________________________
    VERSION 1.2.3.4
    DESCRIPTION
        long_arg____________________________________________________________
    HOMEPAGE_URL
        long_arg____________________________________________________________
    LANGUAGES
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)
