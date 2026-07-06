mod argument_schema;
mod configuration;
mod custom_command_definition_finder;
mod formatter;
mod keyword_preprocessor;
mod mode;
mod node;
mod parser;
mod sanity_checker;
mod two_words_keyword_isolator;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::{CommandSchemaMapping, CommandSchemas};
    use crate::configuration::Configuration;
    use crate::custom_command_definition_finder::CustomCommand;
    use crate::formatter::UnknownCommandsUsed;
    use crate::mode::Mode;
    use crate::parser::{Error, Parser};
    use crate::sanity_checker::check_equivalence;
    use ignore::WalkBuilder;
    use pyo3::exceptions::PyRuntimeError;
    use pyo3::types::{PyAnyMethods, PyModule};
    use pyo3::{pyfunction, PyResult, Python};
    use std::collections::HashMap;
    use std::fmt::Write;
    use std::io::Write as IoWrite;
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

    fn write_code(path: &Path, code: &str) -> PyResult<()> {
        if is_stdin(path) {
            Ok(to_stdout(code)?)
        } else {
            Ok(std::fs::write(path, code)?)
        }
    }

    fn unknown_command_warning(
        command_name: &str,
        positions: Vec<(usize, usize)>,
        path: &str,
    ) -> String {
        positions.into_iter().fold(
            format!("Warning: unknown command '{command_name}' used at:\n"),
            |mut output, (line, column)| {
                let _ = writeln!(output, "{path}:{line}:{column}");
                output
            },
        )
    }

    fn unknown_command_warnings(unknown_commands: UnknownCommandsUsed, path: &str) -> Vec<String> {
        type Position = (usize, usize);
        let mut result = Vec::<(String, Vec<Position>)>::new();
        for (name, line, column) in unknown_commands {
            match result
                .iter_mut()
                .find(|(command, _)| command.as_str() == name)
            {
                None => {
                    result.push((name, vec![(line, column)]));
                }
                Some((_, positions)) => {
                    positions.push((line, column));
                }
            }
        }

        result
            .into_iter()
            .map(|(command, positions)| unknown_command_warning(&command, positions, path))
            .collect()
    }

    fn fromfile(path: &Path) -> &str {
        if is_stdin(path) {
            "<stdin>"
        } else {
            path.to_str().unwrap_or("---")
        }
    }

    fn format_file(
        path: &Path,
        formatter: Option<&Formatter>,
    ) -> PyResult<(String, String, String, Vec<String>)> {
        const BOM: char = '\u{feff}';

        let code = read_code(path)?;
        let (preserve_bom, code) = match code.strip_prefix(BOM) {
            None => (false, code.as_str()),
            Some(code) => (true, code),
        };
        let newlines_style = if code.contains("\r\n") { "\r\n" } else { "\n" };
        let code = code.replace("\r\n", "\n").replace('\r', "\n");
        let (formatted_code, unknown_commands_used) = match formatter {
            None => (code.clone(), vec![]),
            Some(formatter) => formatter.format(code.clone())?,
        };

        let formatted_code = if preserve_bom {
            format!("{BOM}{formatted_code}")
        } else {
            formatted_code
        };

        let path = fromfile(path);
        Ok((
            code,
            formatted_code,
            newlines_style.to_string(),
            unknown_command_warnings(unknown_commands_used, path),
        ))
    }

    type TaskResult = (usize, Vec<String>);
    const SUCCESS: usize = 0;
    const FAIL: usize = 1;

    fn to_stdout(s: &str) -> PyResult<()> {
        print!("{s}");
        Ok(std::io::stdout().flush()?)
    }

    fn forward_to_stdout(after: &str, warnings: Vec<String>) -> PyResult<TaskResult> {
        to_stdout(after)?;
        Ok((SUCCESS, warnings))
    }

    fn rewrite_in_place(
        path: &Path,
        before: &str,
        after: &str,
        newlines_style: &str,
        warnings: Vec<String>,
    ) -> PyResult<TaskResult> {
        if before != after {
            write_code(path, &after.replace('\n', newlines_style))?;
        }

        Ok((SUCCESS, warnings))
    }

    fn wrong_formatting_warning(path: &Path) -> String {
        format!("{} would be reformatted", fromfile(path))
    }

    fn check_formatting(
        path: &Path,
        before: &str,
        after: &str,
        mut warnings: Vec<String>,
    ) -> TaskResult {
        let code = if before == after {
            SUCCESS
        } else {
            warnings.push(wrong_formatting_warning(path));
            FAIL
        };
        (code, warnings)
    }

    fn print_diff(path: &Path, should_colorize: bool, before: &str, after: &str) -> PyResult<()> {
        let result: String = Python::attach(|py| {
            PyModule::import(py, "gersemi.diff")?
                .getattr("get_diff")?
                .call1((path, should_colorize, before, after))?
                .extract()
        })?;

        to_stdout(&result)
    }

    fn show_diff(
        path: &Path,
        should_colorize: bool,
        before: &str,
        after: &str,
        warnings: Vec<String>,
    ) -> PyResult<TaskResult> {
        print_diff(path, should_colorize, before, after)?;
        Ok((SUCCESS, warnings))
    }

    fn check_and_show_diff(
        path: &Path,
        should_colorize: bool,
        before: &str,
        after: &str,
        warnings: Vec<String>,
    ) -> PyResult<TaskResult> {
        let (code, warnings) = check_formatting(path, before, after, warnings);
        print_diff(path, should_colorize, before, after)?;
        Ok((code, warnings))
    }

    fn do_nothing() -> TaskResult {
        (SUCCESS, Vec::new())
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn run_task(
        path: PathBuf,
        formatter: Option<&Formatter>,
        mode: Mode,
        configuration: Configuration,
    ) -> PyResult<TaskResult> {
        let (before, after, newlines_style, unknown_command_warnings) =
            format_file(&path, formatter)?;
        let warnings = if configuration.outcome.warn_about_unknown_commands {
            unknown_command_warnings
        } else {
            Vec::new()
        };

        let (code, warnings) = if formatter.is_none() {
            match mode {
                Mode::ForwardToStdout => forward_to_stdout(&after, warnings)?,
                _ => do_nothing(),
            }
        } else {
            match mode {
                Mode::ForwardToStdout => forward_to_stdout(&after, warnings)?,
                Mode::RewriteInPlace => {
                    rewrite_in_place(&path, &before, &after, &newlines_style, warnings)?
                }
                Mode::CheckFormatting => check_formatting(&path, &before, &after, warnings),
                Mode::ShowDiff => show_diff(
                    &path,
                    configuration.control.color,
                    &before,
                    &after,
                    warnings,
                )?,
                Mode::CheckFormattingAndShowDiff => check_and_show_diff(
                    &path,
                    configuration.control.color,
                    &before,
                    &after,
                    warnings,
                )?,
                _ => do_nothing(),
            }
        };

        Ok((code, warnings))
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
