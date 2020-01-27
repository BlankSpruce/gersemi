from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.command_invocation_dumpers.condition_syntax_command_invocation_dumper import (
    ConditionSyntaxCommandInvocationDumper,
)
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
    FileCommandDumper,
    FindFileCommandDumper,
    FindLibraryCommandDumper,
    FindPackageCommandDumper,
    FindPathCommandDumper,
    FindProgramCommandDumper,
    ForeachCommandDumper,
    FunctionCommandDumper,
    GetDirectoryPropertyCommandDumper,
    GetFilenameComponentCommandDumper,
    GetPropertyCommandDumper,
    IncludeCommandDumper,
    ListCommandDumper,
    MacroCommandDumper,
    MarkAsAdvancedCommandDumper,
    MathCommandDumper,
    MessageCommandDumper,
    SeparateArgumentsCommandDumper,
    SetPropertyCommandDumper,
    StringCommandDumper,
)


class CommandInvocationDumper(BaseCommandInvocationDumper):
    known_command_mapping = {
        "cmake_host_system_information": CMakeHostSysteInformationCommandDumper,
        "cmake_parse_arguments": CMakeParseArgumentsCommandDumper,
        "configure_file": ConfigureFileCommandDumper,
        "elseif": ConditionSyntaxCommandInvocationDumper,
        "else": ConditionSyntaxCommandInvocationDumper,
        "endif": ConditionSyntaxCommandInvocationDumper,
        "endforeach": EndForeachCommandDumper,
        "endfunction": EndFunctionCommandDumper,
        "endmacro": EndMacroCommandDumper,
        "endwhile": ConditionSyntaxCommandInvocationDumper,
        "execute_process": ExecuteProcessCommandDumper,
        "file": FileCommandDumper,
        "find_file": FindFileCommandDumper,
        "find_library": FindLibraryCommandDumper,
        "find_package": FindPackageCommandDumper,
        "find_path": FindPathCommandDumper,
        "find_program": FindProgramCommandDumper,
        "foreach": ForeachCommandDumper,
        "function": FunctionCommandDumper,
        "get_directory_property": GetDirectoryPropertyCommandDumper,
        "get_filename_component": GetFilenameComponentCommandDumper,
        "get_property": GetPropertyCommandDumper,
        "if": ConditionSyntaxCommandInvocationDumper,
        "include": IncludeCommandDumper,
        "list": ListCommandDumper,
        "macro": MacroCommandDumper,
        "mark_as_advanced": MarkAsAdvancedCommandDumper,
        "math": MathCommandDumper,
        "message": MessageCommandDumper,
        "separate_arguments": SeparateArgumentsCommandDumper,
        "set_directory_properties": SetDirectoryPropertiesCommandDumper,
        "set_property": SetPropertyCommandDumper,
        "set": SetCommandDumper,
        "string": StringCommandDumper,
        "while": ConditionSyntaxCommandInvocationDumper,
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
