from gersemi.enum_with_metadata import EnumWithMetadata


class PrintConfigKind(EnumWithMetadata):
    Minimal = dict(
        value="minimal",
        description="""
    With "minimal" prints source of outcome configuration (configuration file or defaults)
    and the options that differ from defaults.
        """,
        title="Minimal",
    )
    Verbose = dict(
        value="verbose",
        description="""
    With "verbose" prints source of outcome configuration (configuration file or defaults),
    files for which this configuration is applicable and complete listing of options.
        """,
        title="Verbose",
    )
    Default = dict(
        value="default",
        description="""
    With "default" prints outcome configuration with default values.
        """,
        title="Default",
    )


def print_config_kind(s) -> PrintConfigKind:
    if s in [e.value for e in PrintConfigKind]:
        return PrintConfigKind(s)

    return s
