mod argument_schema;
mod configuration;
mod custom_command_definition_finder;
mod formatter;
mod keyword_preprocessor;
mod node;
mod parser;
mod sanity_checker;
mod two_words_keyword_isolator;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::{CommandSchemaMapping, CommandSchemas};
    use crate::custom_command_definition_finder::CustomCommand;
    use crate::formatter::UnknownCommandsUsed;
    use crate::parser::{Error, Parser};
    use crate::sanity_checker::check_equivalence;
    use ignore::WalkBuilder;
    use pyo3::exceptions::PyRuntimeError;
    use pyo3::types::{PyAnyMethods, PyModule};
    use pyo3::{pyfunction, PyResult, Python};
    use std::collections::HashMap;
    use std::path::{Path, PathBuf};

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn validate(text: String, schemas: CommandSchemaMapping) -> Result<(), Error> {
        let schemas = CommandSchemas { schemas };
        let parser = Parser::new(text, &schemas);
        parser.start().and(Ok(()))
    }

    fn has_custom_command_definition(code: &str) -> bool {
        let code = code.to_lowercase();
        (code.contains("function") && code.contains("endfunction"))
            || (code.contains("macro") && code.contains("endmacro"))
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn find_custom_command_definitions(
        text: String,
        filepath: String,
    ) -> PyResult<HashMap<String, Vec<CustomCommand>>> {
        if !has_custom_command_definition(&text) {
            return Ok(HashMap::new());
        }

        let schemas = CommandSchemas {
            schemas: HashMap::new(),
        };
        let parser = Parser::new(text, &schemas);
        crate::custom_command_definition_finder::find_custom_command_definitions(&parser, filepath)
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn check_code_equivalence(
        schemas: CommandSchemaMapping,
        before: String,
        after: String,
    ) -> Result<bool, Error> {
        let schemas = CommandSchemas { schemas };
        let before = Parser::new(before, &schemas).start()?;
        let after = Parser::new(after, &schemas).start()?;

        Ok(check_equivalence(before, after))
    }

    #[pymodule_export]
    use crate::formatter::Formatter;

    fn is_stdin(path: &Path) -> bool {
        path.to_str().is_some_and(|value| value == "-")
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn get_files(paths: Vec<PathBuf>, respect_ignore_files: bool) -> PyResult<Vec<PathBuf>> {
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
        for entry in builder
            .require_git(false)
            .standard_filters(respect_ignore_files)
            .build()
        {
            let Ok(entry) = entry else {
                return fail;
            };

            let name = entry.file_name();
            let Some(name) = name.to_str() else {
                return fail;
            };
            if (name == "CMakeLists.txt")
                || (name == "CMakeLists.txt.in")
                || (name.ends_with(".cmake"))
                || (name.ends_with(".cmake.in"))
            {
                result.push(std::path::absolute(entry.into_path())?);
            }
        }

        result.sort();
        result.dedup();
        Ok(result)
    }

    fn read_code(path: &Path) -> PyResult<String> {
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

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn format_file(
        path: PathBuf,
        formatter: Option<&Formatter>,
    ) -> PyResult<(String, String, String, UnknownCommandsUsed)> {
        const BOM: char = '\u{feff}';

        let code = read_code(&path)?;
        let (preserve_bom, code) = match code.strip_prefix(BOM) {
            None => (false, code.as_str()),
            Some(code) => (true, code),
        };
        let newlines_style = if code.contains("\r\n") { "\r\n" } else { "\n" };
        let code = code.replace("\r\n", "\n").replace('\r', "\n");
        let (formatted_code, warnings) = match formatter {
            None => (code.clone(), vec![]),
            Some(formatter) => formatter.format(code.clone())?,
        };

        let formatted_code = if preserve_bom {
            format!("{BOM}{formatted_code}")
        } else {
            formatted_code
        };

        Ok((code, formatted_code, newlines_style.to_string(), warnings))
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
