from enum import Enum


class Mode(Enum):
    ForwardToStdout = 0
    RewriteInPlace = 1
    CheckFormatting = 2
    ShowDiff = 3
    PrintConfig = 4
    CheckFormattingAndShowDiff = 5


def get_mode(args) -> Mode:
    if args.check_formatting and args.show_diff:
        return Mode.CheckFormattingAndShowDiff
    if args.show_diff:
        return Mode.ShowDiff
    if args.check_formatting:
        return Mode.CheckFormatting
    if args.in_place:
        return Mode.RewriteInPlace
    if args.print_config:
        return Mode.PrintConfig
    return Mode.ForwardToStdout
