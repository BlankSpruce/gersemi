import argparse
from dataclasses import fields
import pathlib
import sys
from lark import __version__ as lark_version
from gersemi.configuration import (
    normalize_definitions,
    normalize_extensions,
    sanitize_list_expansion,
    ControlConfiguration,
    OutcomeConfiguration,
    ListExpansion,
    indent_type,
    workers_type,
)
from gersemi.configuration_reports import default_report
from gersemi.print_config_kind import PrintConfigKind, print_config_kind
from gersemi.return_codes import SUCCESS, FAIL
from gersemi.runner import run, print_to_stderr
from gersemi.__version__ import __title__, __version__

MISSING = "(missing)"


try:
    from colorama import __version__ as colorama_version

except ImportError:
    colorama_version = MISSING


class ShowVersion(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(f"{__title__} {__version__}")
        print(f"lark {lark_version}")
        print(f"colorama {colorama_version}")
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
    It can be used together with --diff.
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
        help="""
    Show diff on stdout for each formatted file instead.
    It can be used together with --check.
        """,
    )
    modes_group.add_argument(
        "--print-config",
        dest="print_config",
        choices=[e.value for e in PrintConfigKind],
        help=f"""Print configuration for files.
        {" ".join(map(lambda attr: attr.description, PrintConfigKind))}
        Command line arguments are taken into consideration just
        as they would be for formatting.
        When configuration file is found values in "definitions" are printed as relative
        paths, otherwise absolute paths are printed.
        Output can be placed in .gersemirc file verbatim.""",
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
        default=None,
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
    [default: warnings enabled, same as --warn-about-unknown-commands]
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
    outcome_configuration_group.add_argument(
        "--extensions",
        dest="extensions",
        metavar="extension-name-or-path",
        default=None,
        nargs="+",
        type=str,
        help=outcome_conf_doc["extensions"],
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
        action=toggle_with_no_prefix,
        nargs=0,
        default=None,
        help=f"{control_conf_doc['quiet']} [default: don't skip, same as --no-quiet]",
    )

    if colorama_version == MISSING:
        warn_about_missing_colorama = " Warning: missing colorama."
    else:
        warn_about_missing_colorama = ""

    control_configuration_group.add_argument(
        "--color",
        "--no-color",
        dest="color",
        action=toggle_with_no_prefix,
        nargs=0,
        default=None,
        help=f"""
        {control_conf_doc['color']}
        {warn_about_missing_colorama}
        [default: don't colorize diff, same as --no-color]
        """,
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
    [default: cache enabled, same as --cache]
        """,
    )
    control_configuration_group.add_argument(
        "--config",
        dest="configuration_file",
        type=pathlib.Path,
        default=None,
        help=f"""
    {control_conf_doc["configuration_file"]}
    [default: omitted]
        """,
    )
    control_configuration_group.add_argument(
        "--warnings-as-errors",
        dest="warnings_as_errors",
        action="store_true",
        default=None,
        help=control_conf_doc["warnings_as_errors"],
    )

    parser.add_argument(
        dest="sources",
        metavar="src",
        nargs="*",
        type=pathlib.Path,
        help="""
    File or directory to format. When directory is provided then CMakeLists.txt
    and files with .cmake extension are automatically discovered.
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
    args.extensions = normalize_extensions(args.extensions)
    args.list_expansion = sanitize_list_expansion(args.list_expansion)
    args.print_config = print_config_kind(args.print_config)


def error(text):
    print_to_stderr(text)
    sys.exit(FAIL)


def main():
    try:
        argparser = create_argparser()
        args = argparser.parse_args()

        if args.print_config == PrintConfigKind.Default.value:
            print(default_report())
            sys.exit(SUCCESS)

        postprocess_args(args)

        if any(map(is_stdin_mixed_with_file_input, [args.sources, args.definitions])):
            error("Don't mix stdin with file input")

        if len(args.sources) < 1:
            sys.exit(SUCCESS)

        sys.exit(run(args))
    except Exception as exception:  # pylint: disable=broad-exception-caught
        error(exception)


if __name__ == "__main__":
    main()
