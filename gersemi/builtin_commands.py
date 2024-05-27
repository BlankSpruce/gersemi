import os


def is_not_comment_or_empty(s):
    return not (s.startswith("#") or len(s) == 0)


def get_builtin_commands():
    HERE = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(HERE, "builtin_commands"), "r", encoding="utf-8") as f:
        return {
            item.lower(): item
            for item in filter(is_not_comment_or_empty, f.read().splitlines())
        }


BUILTIN_COMMANDS = get_builtin_commands()
