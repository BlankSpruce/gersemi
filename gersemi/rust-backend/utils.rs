use crate::argument_schema::CommandSchemaMapping;
use crate::configuration::{ControlConfiguration, Extension, OutcomeConfiguration};
use crate::runner::is_stdin;
use ignore::types::{Types, TypesBuilder};
use ignore::WalkBuilder;
use pyo3::exceptions::PyRuntimeError;
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

fn cmake_types() -> Result<Types, ignore::Error> {
    let mut result = TypesBuilder::new();
    result.add("cmake", "CMakeLists.txt")?;
    result.add("cmake", "*.cmake")?;
    result.add("cmake", "CMakeLists.txt.in")?;
    result.add("cmake", "*.cmake.in")?;
    result.select("cmake");
    let result = result.build();

    if let Err(ref err) = result {
        println!("dbg: {err:?}");
    }

    result
}

pub fn get_files(paths: Vec<PathBuf>, respect_ignore_files: bool) -> PyResult<Vec<PathBuf>> {
    if paths.iter().find(|path| is_stdin(path)).is_some() {
        return Ok(paths);
    }

    let Some(first) = paths.first() else {
        return Ok(vec![]);
    };

    let mut builder = WalkBuilder::new(first);
    for path in paths.into_iter().skip(1) {
        builder.add(path);
    }

    let fail = Err(PyRuntimeError::new_err("Failed to find files"));
    let mut result = Vec::<PathBuf>::new();

    let Ok(type_matcher) = cmake_types() else {
        return fail;
    };

    for entry in builder
        .require_git(false)
        .standard_filters(respect_ignore_files)
        .types(type_matcher)
        .build()
    {
        let Ok(entry) = entry else {
            return fail;
        };

        let p = entry.into_path();
        if p.is_dir() {
            continue;
        }

        result.push(std::path::absolute(p)?);
    }

    result.sort();
    result.dedup();
    Ok(result)
}
