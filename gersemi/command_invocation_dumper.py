from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.command_invocation_dumpers.set_directory_properties_command import (
    SetDirectoryPropertiesCommandDumper,
)
from gersemi.command_invocation_dumpers.set_command import SetCommandDumper
from gersemi.command_invocation_dumpers.scripting_command_dumpers import (
    CMakeHostSysteInformationCommandDumper,
    CMakeParseArgumentsCommandDumper,
    ConfigureFileCommandDumper,
    EndForeachCommandDumper,
    EndFunctionCommandDumper,
    EndMacroCommandDumper,
    ExecuteProcessCommandDumper,
    ForeachCommandDumper,
    FunctionCommandDumper,
    GetDirectoryPropertyCommandDumper,
    GetFilenameComponentCommandDumper,
    GetPropertyCommandDumper,
    IncludeCommandDumper,
    MacroCommandDumper,
    MarkAsAdvancedCommandDumper,
    MathCommandDumper,
    MessageCommandDumper,
    SeparateArgumentsCommandDumper,
    SetPropertyCommandDumper,
)


class CommandInvocationDumper(BaseCommandInvocationDumper):
    known_command_mapping = {
        "cmake_host_system_information": CMakeHostSysteInformationCommandDumper,
        "cmake_parse_arguments": CMakeParseArgumentsCommandDumper,
        "configure_file": ConfigureFileCommandDumper,
        "endforeach": EndForeachCommandDumper,
        "endfunction": EndFunctionCommandDumper,
        "endmacro": EndMacroCommandDumper,
        "execute_process": ExecuteProcessCommandDumper,
        "foreach": ForeachCommandDumper,
        "function": FunctionCommandDumper,
        "get_directory_property": GetDirectoryPropertyCommandDumper,
        "get_filename_component": GetFilenameComponentCommandDumper,
        "get_property": GetPropertyCommandDumper,
        "include": IncludeCommandDumper,
        "macro": MacroCommandDumper,
        "mark_as_advanced": MarkAsAdvancedCommandDumper,
        "math": MathCommandDumper,
        "message": MessageCommandDumper,
        "separate_arguments": SeparateArgumentsCommandDumper,
        "set_directory_properties": SetDirectoryPropertiesCommandDumper,
        "set_property": SetPropertyCommandDumper,
        "set": SetCommandDumper,
    }

    def _patch_dumper(self, patch):
        original_dumper = type(self)

        class Impl(patch, original_dumper):
            pass

        return Impl(self.alignment)

    def _get_patch(self, command_name):
        return self.known_command_mapping.get(command_name, None)

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(command_name)
        if patch is None:
            return super().format_command(tree)
        return self._patch_dumper(patch).format_command(tree)
