from dataclasses import dataclass


@dataclass
class Configuration:
    line_length: int
    preserve_custom_command_formatting: bool
