use crate::argument_schema::CommandSchemaMapping;
use crate::configuration::{ControlConfiguration, Extension, OutcomeConfiguration};
use crate::runner::is_stdin;
use pyo3::types::{PyAnyMethods, PyModule};
use pyo3::{Py, PyAny, PyResult, Python};
use std::io::{stdin, Read};
use std::path::{Path, PathBuf};
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
        let mut buf = String::new();
        stdin().read_to_string(&mut buf)?;
        Ok(buf)
    } else {
        Ok(std::fs::read_to_string(path)?)
    }
}

pub fn normalize_newlines(code: &str) -> String {
    code.replace("\r\n", "\n").replace('\r', "\n")
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

pub fn make_control_configuration(args: &Py<PyAny>) -> PyResult<ControlConfiguration> {
    Python::attach(|py| {
        PyModule::import(py, "gersemi.configuration")?
            .getattr("make_control_configuration")?
            .call1((args,))?
            .extract()
    })
}

pub fn make_outcome_configuration(
    configuration_file: Option<&PathBuf>,
    args: &Py<PyAny>,
) -> PyResult<OutcomeConfiguration> {
    Python::attach(|py| {
        PyModule::import(py, "gersemi.configuration")?
            .getattr("make_outcome_configuration")?
            .call1((configuration_file, args))?
            .extract()
    })
}

pub fn print_configuration_report(
    configuration_file: Option<PathBuf>,
    files: Vec<PathBuf>,
    args: &Py<PyAny>,
) -> PyResult<()> {
    Python::attach(|py| {
        let _ = PyModule::import(py, "gersemi.configuration_reports")?
            .getattr("print_configuration_report")?
            .call1((configuration_file, files, args))?;
        Ok(())
    })
}
