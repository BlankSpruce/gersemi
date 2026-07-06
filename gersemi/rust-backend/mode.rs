use pyo3::exceptions::PyRuntimeError;
use pyo3::types::PyAnyMethods;
use pyo3::{Borrowed, FromPyObject, PyAny, PyErr};

#[derive(Debug)]
pub enum Mode {
    ForwardToStdout,
    RewriteInPlace,
    CheckFormatting,
    ShowDiff,
    PrintConfig,
    CheckFormattingAndShowDiff,
}

impl FromPyObject<'_, '_> for Mode {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let value: usize = obj.getattr("value")?.extract()?;
        match value {
            0 => Ok(Self::ForwardToStdout),
            1 => Ok(Self::RewriteInPlace),
            2 => Ok(Self::CheckFormatting),
            3 => Ok(Self::ShowDiff),
            4 => Ok(Self::PrintConfig),
            5 => Ok(Self::CheckFormattingAndShowDiff),
            _ => Err(PyRuntimeError::new_err("Invalid Mode")),
        }
    }
}
