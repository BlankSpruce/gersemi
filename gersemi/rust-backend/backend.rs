mod parser;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::parser::{BlockDefinitions, Error, ErrorType, Node, Parser};
    use pyo3::prelude::*;
    use pyo3::sync::PyOnceLock;
    use pyo3::types::PyType;

    fn convert(py: Python<'_>, node: Node) -> PyResult<Bound<'_, PyAny>> {
        static TREE: PyOnceLock<Py<PyType>> = PyOnceLock::new();
        static TOKEN: PyOnceLock<Py<PyType>> = PyOnceLock::new();
        match node {
            Node::Tree { data, children } => TREE.import(py, "gersemi.types", "Tree")?.call1((
                data,
                children
                    .into_iter()
                    .map(|child| convert(py, child).unwrap())
                    .collect::<Vec<_>>(),
            )),
            Node::Token {
                type_,
                value,
                line,
                column,
            } => TOKEN
                .import(py, "gersemi.types", "Token")?
                .call1((type_, value, line, column)),
        }
    }

    pyo3::import_exception!(gersemi.exceptions, GenericParsingError);
    pyo3::import_exception!(gersemi.exceptions, UnbalancedBlock);
    pyo3::import_exception!(gersemi.exceptions, UnbalancedBrackets);
    pyo3::import_exception!(gersemi.exceptions, UnbalancedParentheses);

    fn raise_exception(error: Error) -> PyErr {
        match error.error_type {
            ErrorType::GenericParsingError => {
                GenericParsingError::new_err((error.explanation, error.line, error.column))
            }
            ErrorType::UnbalancedBlock => {
                UnbalancedBlock::new_err((error.explanation, error.line, error.column))
            }
            ErrorType::UnbalancedBrackets => {
                UnbalancedBrackets::new_err((error.explanation, error.line, error.column))
            }
            ErrorType::UnbalancedParentheses => {
                UnbalancedParentheses::new_err((error.explanation, error.line, error.column))
            }
        }
    }

    #[pyfunction]
    fn parse(
        py: Python<'_>,
        text: String,
        blocks: BlockDefinitions,
        known_commands: Vec<String>,
    ) -> PyResult<Bound<'_, PyAny>> {
        let parser = Parser::new(text, blocks, known_commands);

        match parser.start() {
            Ok(node) => convert(py, node),
            Err(error) => Err(raise_exception(error)),
        }
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
