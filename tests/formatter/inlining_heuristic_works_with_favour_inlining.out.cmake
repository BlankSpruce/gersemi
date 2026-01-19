target_sources(
    TGT__________________________________________________
    PUBLIC FILE_SET FOO FILES BAR
)

target_sources(
    TGT__________________________________________________
    PUBLIC
        FILE_SET FOO FILES BAR BAZ
)

target_sources(
    TGT__________________________________________________
    PUBLIC FOO BAR BAZ QUX
)

target_sources(
    TGT__________________________________________________
    PUBLIC
        FOO
        BAR
        BAZ
        QUX
        FOO
)

install(
    FILES FOO BAR BAZ QUX______________________________
    PERMISSIONS FOO BAR BAZ QUX
)

install(
    FILES
        FOO
        BAR
        BAZ
        QUX
        FOO
    PERMISSIONS FOO BAR BAZ QUX
)

install(
    FILES
        FOO
        BAR
        BAZ
        QUX
        FOO
    PERMISSIONS
        FOO
        BAR
        BAZ
        QUX
        FOO
)
