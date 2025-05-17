from collections.abc import Mapping, Collection
from contextlib import contextmanager
from functools import lru_cache
import importlib
import string
from gersemi.builtin_commands import preprocess_definitions
from gersemi.extension_type import FileExtension
from gersemi.keywords import AnyMatcher


class VerificationFailure(Exception):
    pass


PROPERTIES_WITH_KEYWORDS = {
    "options",
    "one_value_keywords",
    "multi_value_keywords",
}
PROPERTIES_WITH_POSITIONAL_ARGUMENTS = {
    "front_positional_arguments",
    "back_positional_arguments",
}

IDENTIFIER_START = string.ascii_letters + "_"


def is_identifier(identifier):
    return (len(identifier) > 0) and (identifier[0] in IDENTIFIER_START)


class Verifier:
    def __init__(self, extension):
        self.base = f"{extension.qualified_name}:command_definitions"

    @contextmanager
    def element(self, name):
        old = self.base
        try:
            self.base = f"{self.base}[{repr(name)}]"
            yield self
        finally:
            self.base = old

    def fail(self, reason):
        raise VerificationFailure(f"{self.base}: {reason}")

    def verify_collection_of_arguments(self, collection):
        if not isinstance(collection, Collection):
            self.fail(f"is not a collection of strings ({repr(collection)})")

        for index, item in enumerate(collection):
            if not isinstance(item, str):
                with self.element(index):
                    self.fail(f"argument ({repr(item)}) has to be a string")

    def verify_identifier(self, thing, keyword):
        if isinstance(keyword, tuple):
            for index, part in enumerate(keyword):
                self.verify_identifier(f"{thing}[{index}]", part)

            return

        if isinstance(keyword, AnyMatcher):
            return

        if not isinstance(keyword, str):
            self.fail(f"{thing} ({repr(keyword)}) has to be a string")

        if not is_identifier(keyword):
            self.fail(
                f"{thing} ({repr(keyword)}) has to start with a letter or underscore"
            )

    def verify_collection_of_keywords(self, collection):
        if not isinstance(collection, Collection):
            self.fail(f"is not a collection of strings ({repr(collection)})")

        for keyword in collection:
            self.verify_identifier("keyword", keyword)

    def verify_is_mapping(self, thing):
        if not isinstance(thing, Mapping):
            self.fail("is not a mapping")

    def verify_section(self, section):
        self.verify_is_mapping(section)

        for p in PROPERTIES_WITH_POSITIONAL_ARGUMENTS:
            with self.element(p):
                self.verify_collection_of_arguments(section.get(p, []))

        for p in PROPERTIES_WITH_KEYWORDS:
            with self.element(p):
                self.verify_collection_of_keywords(section.get(p, []))

        subsections = section.get("sections", {})
        with self.element("sections"):
            self.verify_is_mapping(subsections)

            for keyword, subsection in subsections.items():
                self.verify_identifier("keyword", keyword)

                with self.element(keyword):
                    self.verify_section(subsection)

    def verify_signatures(self, signatures):
        self.verify_is_mapping(signatures)

        for signature_name, signature in signatures.items():
            self.verify_identifier("signature", signature_name)
            with self.element(signature_name):
                self.verify_section(signature)

    def verify_command(self, name, definition):
        self.verify_identifier("command name", name)

        with self.element(name):
            self.verify_is_mapping(definition)

            if "signatures" in definition:
                with self.element("signatures"):
                    self.verify_signatures(definition["signatures"])
            else:
                self.verify_section(definition)

    def __call__(self, thing):
        self.verify_is_mapping(thing)

        for name, definition in thing.items():
            self.verify_command(name, definition)


def verify(extension, thing):
    verifier = Verifier(extension)
    verifier(thing)


def load_extension(extension):
    if isinstance(extension, FileExtension):
        spec = importlib.util.spec_from_file_location(str(extension), extension.path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        module = importlib.import_module(f"gersemi_{extension}")

    return module


@lru_cache(maxsize=None)
def load_definitions_from_extension(extension):
    try:
        module = load_extension(extension)
    except ModuleNotFoundError:
        return None, f"Missing extension {extension.name}"

    try:
        command_definitions = module.command_definitions
    except AttributeError:
        return (
            None,
            f"Extension {extension.name} doesn't implement command_definitions",
        )

    try:
        verify(extension, command_definitions)
    except VerificationFailure as failure:
        return (
            None,
            f"""Verification failed for extension {extension.name}:
{failure}""",
        )

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
