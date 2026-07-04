from tests.fixtures.app import fail, success


def test_invalid_source_path(app, testfiles):
    source = (testfiles / "this-source-really-doesnt-exist.cmake").resolve()
    assert app("--check", source) == fail(
        stdout="",
        stderr=f"""Source path doesn't exist: {source}
""",
    )


def test_invalid_definition_path(app, testfiles):
    source = testfiles.resolve()
    definition = (testfiles / "this-definition-really-doesnt-exist.cmake").resolve()
    assert app("--definitions", definition, "--check", source) == fail(
        stdout="",
        stderr=f"""Definition path doesn't exist: {definition}
""",
    )


def test_invalid_extension_path(app, testfiles):
    source = testfiles.resolve()
    extension = (testfiles / "this-extension-really-doesnt-exist.py").resolve()
    assert app("--extensions", extension, "--check", source) == fail(
        stdout="",
        stderr=f"""Extension path doesn't exist: {extension}
""",
    )


def test_invalid_extension_module(app, testfiles):
    source = testfiles.resolve()
    extension = "this_extension_really_doesnt_exist"
    assert app("--extensions", extension, "--check", source) == fail(
        stdout="",
        stderr=f"""Missing extension {extension}
""",
    )


def test_invalid_definition_code(app, testfiles):
    definition = (testfiles / "invalid_definition.cmake").resolve()
    source = (testfiles / "formatted_file.cmake").resolve()
    with open(definition, "w", encoding="utf-8") as f:
        f.write("""function(foo)
endfunction(""")

    assert app("--definitions", definition, "--check", source) == success(
        stdout="",
        stderr=f"""{definition}:2:14: unbalanced parentheses
endfunction(
             ^

""",
    )
