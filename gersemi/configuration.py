from dataclasses import dataclass


@dataclass
class Configuration:
    line_length: int
    enable_experimental_features: bool
    preserve_custom_command_formatting: bool
