use crate::cache::Cache;
use crate::custom_command_definition_finder::CustomCommand;
use crate::diff::print_diff;
use crate::formatter::Formatter;
use crate::gersemi_rust_backend::{find_custom_command_definitions, get_files};
use crate::mode::Mode;
use crate::python_side::{get_just_schemas, read_code};
use crate::{configuration::Configuration, formatter::UnknownCommandsUsed};
use pyo3::{pyclass, pymethods, PyResult, Python};
use std::fmt::Write;
use std::io::Write as IoWrite;
use std::path::{Path, PathBuf};

pub fn is_stdin(path: &Path) -> bool {
    path.to_str().is_some_and(|value| value == "-")
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

pub fn fromfile(path: &Path) -> &str {
    if is_stdin(path) {
        "<stdin>"
    } else {
        path.to_str().unwrap_or("---")
    }
}

pub fn tofile(path: &Path) -> &str {
    if is_stdin(path) {
        "<stdout>"
    } else {
        path.to_str().unwrap_or("---")
    }
}

#[pyclass]
pub struct WarningSink {
    quiet: bool,
    #[pyo3(get)]
    pub at_least_one_warning_issued: bool,
    records: Vec<String>,
}

#[pymethods]
impl WarningSink {
    #[new]
    fn new(quiet: bool) -> Self {
        Self {
            quiet,
            at_least_one_warning_issued: false,
            records: Vec::new(),
        }
    }

    pub fn __call__(&mut self, s: String) {
        self.at_least_one_warning_issued = true;
        if !self.quiet {
            self.records.push(s);
        }
    }

    fn flush(&self) {
        for record in &self.records {
            eprintln!("{record}");
        }
    }
}

pub struct Runner<'a> {
    pub mode: Mode,
    pub configuration: Configuration,
    pub warning_sink: Option<&'a mut WarningSink>,
    pub cache: Option<&'a mut Cache>,
}

type TaskResult = (usize, Vec<String>);
const SUCCESS: usize = 0;
const FAIL: usize = 1;
const INTERNAL_ERROR: usize = 123;

pub fn to_stdout(s: &str) -> PyResult<()> {
    print!("{s}");
    Ok(std::io::stdout().flush()?)
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

type Definitions = Vec<(String, Vec<CustomCommand>)>;

impl Runner<'_> {
    fn run_task_impl(
        &mut self,
        path: &Path,
        formatter: Option<&Formatter>,
    ) -> PyResult<(usize, bool)> {
        let (before, after, newlines_style, unknown_command_warnings) =
            format_file(path, formatter)?;
        let warnings = if self.configuration.outcome.warn_about_unknown_commands {
            unknown_command_warnings
        } else {
            Vec::new()
        };

        let (code, warnings) = if formatter.is_none() {
            match self.mode {
                Mode::ForwardToStdout => forward_to_stdout(&after, warnings)?,
                _ => do_nothing(),
            }
        } else {
            match self.mode {
                Mode::ForwardToStdout => forward_to_stdout(&after, warnings)?,
                Mode::RewriteInPlace => {
                    rewrite_in_place(path, &before, &after, &newlines_style, warnings)?
                }
                Mode::CheckFormatting => check_formatting(path, &before, &after, warnings),
                Mode::ShowDiff => show_diff(
                    path,
                    self.configuration.control.color,
                    &before,
                    &after,
                    warnings,
                )?,
                Mode::CheckFormattingAndShowDiff => check_and_show_diff(
                    path,
                    self.configuration.control.color,
                    &before,
                    &after,
                    warnings,
                )?,
                _ => do_nothing(),
            }
        };

        let has_warnings = if self.configuration.outcome.warn_about_unknown_commands {
            let result = !warnings.is_empty();
            for warning in warnings {
                if let Some(sink) = &mut self.warning_sink {
                    sink.__call__(warning);
                }
            }
            result
        } else {
            false
        };
        Ok((code, has_warnings))
    }

    pub fn run_task(&mut self, path: &Path, formatter: Option<&Formatter>) -> (usize, bool) {
        match self.run_task_impl(path, formatter) {
            Ok(ok) => ok,
            Err(err) => {
                if let Some(sink) = &mut self.warning_sink {
                    sink.__call__(format!(
                        "{}: {}",
                        path.to_str().unwrap_or("---"),
                        Python::attach(|py| err.value(py).to_string())
                    ));
                }
                (INTERNAL_ERROR, false)
            }
        }
    }

    pub fn handle_already_formatted_files(&mut self, files: &[PathBuf]) -> Vec<usize> {
        files
            .iter()
            .map(|f| {
                let (code, _) = self.run_task(f, None);
                code
            })
            .collect()
    }

    fn check_conflicting_definitions(&mut self, defs: &Definitions) {
        let Some(sink) = &mut self.warning_sink else {
            return;
        };

        for (name, info) in defs {
            if info.len() <= 1 {
                continue;
            }

            let mut warning = format!("Warning: conflicting definitions for '{name}':");
            let mut locations: Vec<_> = info.iter().map(|(_, location)| location).collect();
            locations.sort();

            for (index, location) in (0..).zip(locations) {
                let kind = if index == 0 { "(used)   " } else { "(ignored)" };
                let _ = write!(warning, "\n{kind} {location}");
            }
            sink.__call__(warning);
        }
    }

    fn should_cache(&self) -> bool {
        self.cache.is_some()
            && matches!(
                self.mode,
                Mode::CheckFormatting | Mode::CheckFormattingAndShowDiff | Mode::RewriteInPlace
            )
    }

    pub fn handle_files_to_format(
        &mut self,
        files: Vec<PathBuf>,
        configuration: Configuration,
    ) -> PyResult<Vec<usize>> {
        let definitions = self.find_all_custom_command_definitions()?;
        let definition_schemas = get_just_schemas(definitions)?;
        let configuration_summary = self.configuration.outcome.summarize()?;
        let formatter = Formatter::new(configuration, definition_schemas)?;
        let formatter = Some(&formatter);

        let should_cache = self.should_cache();
        let mut result = Vec::<usize>::new();
        let mut files_to_cache = Vec::<PathBuf>::new();

        for f in files {
            let (code, has_warnings) = self.run_task(&f, formatter);
            result.push(code);

            if should_cache && (code == SUCCESS) && (!is_stdin(&f)) && (!has_warnings) {
                files_to_cache.push(f);
            }
        }

        if let Some(cache) = &self.cache {
            cache.store_files(&configuration_summary, files_to_cache);
        }
        Ok(result)
    }

    pub fn find_all_custom_command_definitions(&mut self) -> PyResult<Definitions> {
        let mut result = Definitions::new();

        for f in get_files(
            self.configuration.outcome.definitions.clone(),
            self.configuration.control.respect_ignore_files,
        )? {
            let code = read_code(&f)?;
            let path = f.to_str().unwrap_or("---");
            let defs = match find_custom_command_definitions(code, path.to_string()) {
                Err(err) => {
                    if let Some(sink) = &mut self.warning_sink {
                        sink.__call__(format!(
                            "{path}:{}",
                            Python::attach(|py| err.value(py).to_string())
                        ));
                    }
                    continue;
                }
                Ok(defs) => defs,
            };

            for (name, mut info) in defs {
                match result
                    .iter_mut()
                    .find(|(command, _)| command.as_str() == name)
                {
                    None => {
                        result.push((name, info));
                    }
                    Some((_, values)) => {
                        values.append(&mut info);
                    }
                }
            }
        }

        self.check_conflicting_definitions(&result);

        Ok(result)
    }
}
