use crate::argument_schema::CommandSchemaMapping;
use crate::configuration::Extension;
use crate::custom_command_definition_finder::CustomCommand;
use crate::runner::is_stdin;
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

pub fn load_definitions_from_extensions(
    extensions: &Vec<Extension>,
) -> PyResult<CommandSchemaMapping> {
    Python::attach(|py| {
        PyModule::import(py, "gersemi.extensions")?
            .getattr("load_definitions_from_extensions")?
            .call1((extensions,))?
            .extract()
    })
}

pub fn get_just_schemas(
    definitions: Vec<(String, Vec<CustomCommand>)>,
) -> PyResult<CommandSchemaMapping> {
    Python::attach(|py| {
        PyModule::import(py, "gersemi.custom_command_definition_finder")?
            .getattr("get_just_definitions")?
            .call1((definitions,))?
            .extract()
    })
}
