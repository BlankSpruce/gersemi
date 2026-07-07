use crate::argument_schema::CommandSchemaMapping;
use crate::runner::{is_stdin, to_stdout};
use pyo3::types::{PyAnyMethods, PyModule};
use pyo3::{PyResult, Python};
use std::path::Path;
use std::sync::LazyLock;

pub fn builtin_schemas() -> &'static CommandSchemaMapping {
    static RESULT: LazyLock<CommandSchemaMapping> = LazyLock::new(|| {
        Python::attach(|py| {
            PyModule::import(py, "gersemi.builtin_commands")?
                .getattr("_builtin_commands")?
                .extract()
        })
        .unwrap()
    });
    &RESULT
}

pub fn read_code(path: &Path) -> PyResult<String> {
    if is_stdin(path) {
        Python::attach(|py| {
            PyModule::import(py, "gersemi.utils")?
                .getattr("StdinWrapper")?
                .getattr("read")?
                .call0()?
                .extract()
        })
    } else {
        Ok(std::fs::read_to_string(path)?)
    }
}

pub fn print_diff(path: &Path, should_colorize: bool, before: &str, after: &str) -> PyResult<()> {
    let result: String = Python::attach(|py| {
        PyModule::import(py, "gersemi.diff")?
            .getattr("get_diff")?
            .call1((path, should_colorize, before, after))?
            .extract()
    })?;

    to_stdout(&result)
}
