from dataclasses import asdict, fields
import os
from pathlib import Path
from typing import Iterable, Optional
from gersemi.configuration import (
    make_configuration_file,
    OutcomeConfiguration,
)
from gersemi.extensions import load_definitions_from_extension


NL = "\n"


def report_header(configuration_file: Optional[Path]) -> str:
    if configuration_file is None:
        based_on = "defaults"
    else:
        based_on = f"{configuration_file.resolve()}"

    return f"## Outcome configuration based on {based_on}"


def prepare_configuration_for_report(
    configuration_file: Optional[Path], configuration: OutcomeConfiguration
):
    result = asdict(configuration)
    if configuration_file is not None:
        result["definitions"] = tuple(
            os.path.relpath(p, configuration_file.parent)
            for p in result.get("definitions", tuple())
        )

    return result


def minimal_report(
    configuration_file: Optional[Path], configuration: OutcomeConfiguration
) -> str:
    c = prepare_configuration_for_report(configuration_file, configuration)
    filtered = {}
    keys = {f.name: f for f in fields(OutcomeConfiguration)}
    for name, value in c.items():
        if value != keys[name].default:
            filtered[name] = value

    if filtered == dict():
        comparison = "none of the defaults are overridden.\n"
    else:
        comparison = f"""following options differ from default configuration:
{make_configuration_file(filtered, add_schema_link=False)}"""

    return f"{report_header(configuration_file)},\n## {comparison}\n"


def make_listing(prefix, things):
    return f"{prefix}{f'{NL}{prefix}'.join(things)}"


def applicable_to_files(files: Iterable[Path]) -> str:
    if Path("-") in files:
        return "## it's applicable to stdin."

    return f"""## it's applicable to these files:
{make_listing("## - ", map(str, files))}
##"""


def verbose_about_extension(extension: str) -> str:
    definitions, error = load_definitions_from_extension(extension)
    if error is None:
        return f"""## - [{extension}] additional recognized commands:
{make_listing("##   - ", sorted(definitions.keys()))}
##"""

    return f"""## - [{extension}] error:
{make_listing("##   ", error.splitlines())}
##"""


def verbose_about_extensions(extensions) -> str:
    if len(extensions) == 0:
        return ""

    return f"""
## About extensions:
{NL.join(map(verbose_about_extension, extensions))}"""


def verbose_report(
    configuration_file: Optional[Path],
    configuration: OutcomeConfiguration,
    target_files: Iterable[Path],
) -> str:
    listing = make_configuration_file(
        prepare_configuration_for_report(configuration_file, configuration),
        add_schema_link=True,
    )

    return f"""{report_header(configuration_file)},
{applicable_to_files(target_files)}{verbose_about_extensions(configuration.extensions)}
{listing}
"""


def default_report():
    return make_configuration_file(
        asdict(OutcomeConfiguration()),
        add_schema_link=True,
    )
