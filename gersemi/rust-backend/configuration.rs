use crate::python_side::load_definitions_from_extensions;
use pyo3::exceptions::PyRuntimeError;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyAnyMethods, PyString, PyType};
use pyo3::{
    Borrowed, Bound, BoundObject, FromPyObject, IntoPyObject, Py, PyAny, PyErr, PyResult, Python,
};
use std::path::PathBuf;
use xxhash_rust::xxh3::xxh3_128;

fn string_enum_value(obj: Borrowed<'_, '_, PyAny>) -> Result<String, PyErr> {
    let value = match obj.getattr("value") {
        Ok(value) => value,
        _ => obj.into_bound(),
    };

    Ok(value.cast::<PyString>()?.str()?.to_string())
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum KeywordFormatter {
    CommandLine,
    Pairs,
}

impl FromPyObject<'_, '_> for KeywordFormatter {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let value = string_enum_value(obj)?;
        match value.as_str() {
            "command_line" => Ok(KeywordFormatter::CommandLine),
            "pairs" => Ok(KeywordFormatter::Pairs),
            _ => Err(PyRuntimeError::new_err("Invalid KeywordFormatter")),
        }
    }
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum KeywordPreprocessor {
    Sort,
    Unique,
    SortAndUnique,
}

impl FromPyObject<'_, '_> for KeywordPreprocessor {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let value = string_enum_value(obj)?;
        match value.as_str() {
            "sort" => Ok(KeywordPreprocessor::Sort),
            "unique" => Ok(KeywordPreprocessor::Unique),
            "sort+unique" => Ok(KeywordPreprocessor::SortAndUnique),
            _ => Err(PyRuntimeError::new_err("Invalid KeywordPreprocessor")),
        }
    }
}

#[derive(Clone, Debug)]
pub struct Tabs;

#[derive(Clone, Debug, FromPyObject)]
pub enum IndentType {
    Spaces(usize),
    Tabs(Tabs),
}

impl IndentType {
    pub fn as_string(&self) -> String {
        match self {
            IndentType::Tabs(_) => "\t".to_string(),
            IndentType::Spaces(spaces) => " ".repeat(*spaces),
        }
    }
}

impl FromPyObject<'_, '_> for Tabs {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        if string_enum_value(obj)? == "tabs" {
            Ok(Tabs)
        } else {
            Err(PyRuntimeError::new_err("Invalid Tabs"))
        }
    }
}

#[derive(Clone, Debug)]
pub enum ListExpansion {
    FavourInlining,
    FavourExpansion,
}

impl FromPyObject<'_, '_> for ListExpansion {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let value = string_enum_value(obj)?;
        match value.as_str() {
            "favour-inlining" => Ok(Self::FavourInlining),
            "favour-expansion" => Ok(Self::FavourExpansion),
            _ => Err(PyRuntimeError::new_err("Invalid ListExpansion")),
        }
    }
}

#[derive(Clone, Debug)]
pub enum SortOrder {
    CaseSensitive,
    CaseInsensitive,
}

impl FromPyObject<'_, '_> for SortOrder {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let value = string_enum_value(obj)?;
        match value.as_str() {
            "case-sensitive" => Ok(Self::CaseSensitive),
            "case-insensitive" => Ok(Self::CaseInsensitive),
            _ => Err(PyRuntimeError::new_err("Invalid ListExpansion")),
        }
    }
}

#[derive(Clone, Debug, FromPyObject)]
pub struct Extension(String);

impl<'py> IntoPyObject<'py> for &Extension {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        static FILE_EXT: PyOnceLock<Py<PyType>> = PyOnceLock::new();
        static MODULE_EXT: PyOnceLock<Py<PyType>> = PyOnceLock::new();
        let value = &self.0;
        if value.ends_with(".py") {
            FILE_EXT
                .import(py, "gersemi.extension_type", "FileExtension")?
                .call1((value,))
        } else {
            MODULE_EXT
                .import(py, "gersemi.extension_type", "ModuleExtension")?
                .call1((value,))
        }
    }
}

#[derive(Clone, Debug, FromPyObject)]
pub struct OutcomeConfiguration {
    #[pyo3(attribute("indent"))]
    pub indent_type: IndentType,
    pub line_length: usize,
    pub list_expansion: ListExpansion,
    pub sort_order: SortOrder,
    #[pyo3(attribute("unsafe"))]
    pub disable_sanity_checks: bool,
    pub warn_about_unknown_commands: bool,
    pub extensions: Vec<Extension>,
    pub definitions: Vec<PathBuf>,
}

#[derive(Clone, FromPyObject)]
pub struct LineRange {
    pub start: usize,
    pub end: usize,
}

#[derive(Clone, FromPyObject)]
#[allow(clippy::struct_excessive_bools)]
pub struct ControlConfiguration {
    pub color: bool,
    pub respect_ignore_files: bool,
    pub line_ranges: Vec<LineRange>,
    pub cache: bool,
    pub cache_dir: PathBuf,
    pub quiet: bool,
    pub warnings_as_errors: bool,
    pub configuration_file: Option<PathBuf>,
}

#[derive(Clone, FromPyObject)]
pub struct Configuration {
    pub outcome: OutcomeConfiguration,
    pub control: ControlConfiguration,
}

impl OutcomeConfiguration {
    pub fn summarize(&self) -> PyResult<String> {
        let extension_schemas = load_definitions_from_extensions(&self.extensions)?;
        let summary = format!("{self:?};{extension_schemas:?}");
        Ok(format!("{:X}", xxh3_128(summary.as_bytes())))
    }
}
