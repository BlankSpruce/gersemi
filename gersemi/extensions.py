from functools import lru_cache
import importlib
from gersemi.builtin_commands import preprocess_definitions


class VerificationFailure(Exception):
    pass


def verify(thing):
    return isinstance(thing, dict)


@lru_cache(maxsize=None)
def load_definitions_from_extension(extension):
    try:
        module = importlib.import_module(f"gersemi_{extension}")
    except ModuleNotFoundError:
        return None, f"Missing extension {extension}"

    try:
        command_definitions = module.command_definitions
    except AttributeError:
        return None, f"Extension {extension} doesn't implement command_definitions"

    if not verify(command_definitions):
        return None, f"Verification failed for extension {extension}"

    return preprocess_definitions(command_definitions), None


def load_definitions_from_extensions(extensions):
    result = {}
    errors = []

    for extension in extensions:
        try:
            definitions, error = load_definitions_from_extension(extension)
            if error is not None:
                errors.append(error)
            else:
                result.update(definitions)
        except Exception as e:  # pylint: disable=broad-exception-caught
            errors.append(str(e))

    if errors:
        raise Exception(  # pylint: disable=broad-exception-raised
            "\n".join(sorted(errors))
        )

    return result
