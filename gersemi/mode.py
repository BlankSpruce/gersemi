from enum import Enum


class Mode(Enum):
    ForwardToStdout = 0
    RewriteInPlace = 1
    CheckFormatting = 2
    ShowDiff = 3


def get_mode(args) -> Mode:
    if args.show_diff:
        return Mode.ShowDiff
    if args.check_formatting:
        return Mode.CheckFormatting
    if args.in_place:
        return Mode.RewriteInPlace
    return Mode.ForwardToStdout
