import argparse
from dataclasses import fields
import pathlib
import sys
from lark import __version__ as lark_version
from gersemi.configuration import (
    make_default_configuration_file,
    normalize_definitions,
    sanitize_list_expansion,
    ControlConfiguration,
    OutcomeConfiguration,
    ListExpansion,
    indent_type,
    workers_type,
)
from gersemi.return_codes import SUCCESS, FAIL
from gersemi.runner import run, print_to_stderr
from gersemi.__version__ import __title__, __version__


class GenerateConfigurationFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(make_default_configuration_file())
        sys.exit(SUCCESS)


class ShowVersion(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(f"{__title__} {__version__}")
        print(f"lark {lark_version}")
        print(f"Python {sys.version}")
        sys.exit(SUCCESS)


def toggle_action(predicate):
    class Impl(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(
                namespace,
                self.dest,
                not predicate(option_string),
            )

            # option_string.startswith("--no-")

    return Impl


toggle_with_no_prefix = toggle_action(lambda s: s.startswith("--no-"))


def create_argparser():
    parser = argparse.ArgumentParser(
        description="A formatter to make your CMake code the real treasure.",
        prog="gersemi",
        add_help=False,
    )
    modes_group = parser.add_argument_group("modes")
    modes_group.add_argument(
        "-c",
        "--check",
        dest="check_formatting",
        action="store_true",
        help=f"""
    Check if files require reformatting.
    Return {SUCCESS} when there's nothing to reformat.
    Return {FAIL} when some files would be reformatted.
            """,
    )
    modes_group.add_argument(
        "-i",
        "--in-place",
        dest="in_place",
        action="store_true",
        help="Format files in-place.",
    )
    modes_group.add_argument(
        "--diff",
        dest="show_diff",
        action="store_true",
        help="Show diff on stdout for each formatted file instead.",
    )
    modes_group.add_argument(
        "--default-config",
        nargs=0,
        action=GenerateConfigurationFile,
        help="Generate default .gersemirc configuration file.",
    )
    modes_group.add_argument(
        "--version",
        nargs=0,
        dest="show_version",
        action=ShowVersion,
        help="Show version.",
    )
    modes_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    outcome_conf_doc: dict[str, str] = {
        item.name: item.metadata["description"] for item in fields(OutcomeConfiguration)
    }
    outcome_configuration_group = parser.add_argument_group(
        title="outcome configuration", description=OutcomeConfiguration.__doc__
    )
    outcome_configuration_group.add_argument(
        "-l",
        "--line-length",
        metavar="INTEGER",
        dest="line_length",
        type=int,
        help=f"{outcome_conf_doc['line_length']} [default: {OutcomeConfiguration.line_length}]",
    )
    outcome_configuration_group.add_argument(
        "--indent",
        metavar="(INTEGER | tabs)",
        dest="indent",
        type=indent_type,
        help=f"{outcome_conf_doc['indent']} [default: {repr(OutcomeConfiguration.indent)}]",
    )
    outcome_configuration_group.add_argument(
        "--unsafe",
        dest="unsafe",
        action="store_true",
        help=outcome_conf_doc["unsafe"],
    )
    outcome_configuration_group.add_argument(
        "--definitions",
        dest="definitions",
        metavar="src",
        default=None,
        nargs="+",
        type=pathlib.Path,
        help=outcome_conf_doc["definitions"],
    )
    outcome_configuration_group.add_argument(
        "--list-expansion",
        dest="list_expansion",
        choices=["favour-inlining", "favour-expansion"],
        help=f"""
    {outcome_conf_doc['list_expansion']}
    {" ".join(map(lambda attr: attr.description, ListExpansion))}
    [default: {OutcomeConfiguration.list_expansion.value}]
            """,
    )
    outcome_configuration_group.add_argument(
        "--warn-about-unknown-commands",
        "--no-warn-about-unknown-commands",
        dest="warn_about_unknown_commands",
        action=toggle_with_no_prefix,
        nargs=0,
        default=None,
        help=f"""
    {outcome_conf_doc["warn_about_unknown_commands"]}
    [default: warnings enabled]
        """,
    )
    outcome_configuration_group.add_argument(
        "--disable-formatting",
        "--enable-formatting",
        dest="disable_formatting",
        action=toggle_action(lambda s: s == "--enable-formatting"),
        nargs=0,
        default=None,
        help=f"""
    {outcome_conf_doc["disable_formatting"]}
    [default: formatting enabled]
        """,
    )

    control_conf_doc: dict[str, str] = {
        item.name: item.metadata["description"] for item in fields(ControlConfiguration)
    }
    control_configuration_group = parser.add_argument_group(
        title="control configuration", description=ControlConfiguration.__doc__
    )
    control_configuration_group.add_argument(
        "-q",
        "--quiet",
        "--no-quiet",
        dest="quiet",
        action="store_true",
        help=f"{control_conf_doc['quiet']} [default: don't skip]",
    )
    control_configuration_group.add_argument(
        "--color",
        "--no-color",
        dest="color",
        action=toggle_with_no_prefix,
        nargs=0,
        default=None,
        help=f"{control_conf_doc['color']} [default: don't colorize diff]",
    )
    control_configuration_group.add_argument(
        "-w",
        "--workers",
        metavar="(INTEGER | max)",
        dest="workers",
        type=workers_type,
        help=f"""
    {control_conf_doc['workers']} [default: {repr(ControlConfiguration.workers)}]
        """,
    )
    control_configuration_group.add_argument(
        "--cache",
        "--no-cache",
        dest="cache",
        action=toggle_with_no_prefix,
        nargs=0,
        default=None,
        help=f"""
    {control_conf_doc["cache"]}
    [default: cache enabled]
        """,
    )

    parser.add_argument(
        dest="sources",
        metavar="src",
        nargs="*",
        type=pathlib.Path,
        help="""
    File or directory to format.
    If only `-` is provided, input is taken from stdin instead.
            """,
    )

    return parser


def is_stdin_mixed_with_file_input(sources):
    if sources is None:
        return False

    return pathlib.Path("-") in sources and len(sources) != 1


def postprocess_args(args):
    args.sources = set(args.sources)
    if args.definitions is not None:
        args.definitions = set(args.definitions)

    args.definitions = normalize_definitions(args.definitions)
    args.list_expansion = sanitize_list_expansion(args.list_expansion)


def main():
    argparser = create_argparser()
    args = argparser.parse_args()
    postprocess_args(args)

    def error(text):
        print_to_stderr(text)
        sys.exit(FAIL)

    if any(map(is_stdin_mixed_with_file_input, [args.sources, args.definitions])):
        error("Don't mix stdin with file input")

    if len(args.sources) < 1:
        sys.exit(SUCCESS)

    try:
        sys.exit(run(args))
    except Exception as exception:  # pylint: disable=broad-exception-caught
        error(exception)


if __name__ == "__main__":
    main()
