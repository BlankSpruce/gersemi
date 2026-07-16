use pyo3::exceptions::PyRuntimeError;
use pyo3::types::PyAnyMethods;
use pyo3::{Borrowed, FromPyObject, Py, PyAny, PyErr, PyResult, Python};
use std::path::PathBuf;

#[derive(Clone, Debug)]
pub enum Mode {
    ForwardToStdout,
    RewriteInPlace,
    CheckFormatting,
    ShowDiff,
    PrintConfig,
    CheckFormattingAndShowDiff,
}

pub struct Args {
    pub obj: Py<PyAny>,
    pub sources: Vec<PathBuf>,
    pub mode: Mode,
}

struct ArgsExtractor<'a> {
    py: Python<'a>,
    obj: &'a Py<PyAny>,
}

enum PrintConfigKind {
    Minimal,
    Verbose,
    Default,
}

impl FromPyObject<'_, '_> for PrintConfigKind {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let value: String = obj.getattr("value")?.extract()?;
        match value.as_str() {
            "minimal" => Ok(Self::Minimal),
            "verbose" => Ok(Self::Verbose),
            "default" => Ok(Self::Default),
            _ => Err(PyRuntimeError::new_err("Invalid PrintConfigKind")),
        }
    }
}

impl ArgsExtractor<'_> {
    fn value<T: for<'a> FromPyObject<'a, 'a, Error = PyErr>>(&self, name: &str) -> PyResult<T> {
        self.obj.getattr(self.py, name)?.extract(self.py)
    }
}

fn get_mode(args: &ArgsExtractor, print_config: Option<&PrintConfigKind>) -> PyResult<Mode> {
    let check_formatting = args.value("check_formatting")?;
    let show_diff = args.value("show_diff")?;
    let result = if check_formatting && show_diff {
        Mode::CheckFormattingAndShowDiff
    } else if show_diff {
        Mode::ShowDiff
    } else if check_formatting {
        Mode::CheckFormatting
    } else if args.value("in_place")? {
        Mode::RewriteInPlace
    } else if print_config.is_some() {
        Mode::PrintConfig
    } else {
        Mode::ForwardToStdout
    };
    Ok(result)
}

impl Args {
    pub fn new(obj: Py<PyAny>) -> PyResult<Self> {
        Python::attach(|py| {
            let args = ArgsExtractor { py, obj: &obj };
            let print_config = args.value::<Option<PrintConfigKind>>("print_config")?;
            let mode = get_mode(&args, print_config.as_ref())?;
            let sources = args.value("sources")?;
            Ok(Self { obj, sources, mode })
        })
    }
}
