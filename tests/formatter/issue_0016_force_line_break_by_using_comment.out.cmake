add_custom_command(
    OUTPUT src.tar.zst
    DEPENDS ${SRC}
    COMMAND
        set -euo pipefail # line comment
        && tar -c src | zstd --ultra -22 > src.tar.zst #
)

add_custom_command(
    OUTPUT src.tar.zst
    DEPENDS ${SRC}
    COMMAND
        set -euo pipefail #[[bracket comment]]
        && tar -c src | zstd --ultra -22 > src.tar.zst #
)

add_custom_target(
    COMMAND
        -a # a
        /b # b
)
