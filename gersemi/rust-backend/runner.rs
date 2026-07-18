use crate::args::Mode;
use crate::cache::Cache;
use crate::diff::print_diff;
use crate::formatter::Formatter;
use crate::utils::{normalize_newlines, read_code};
use crate::warning_sink::warn;
use crate::{configuration::Configuration, formatter::UnknownCommandsUsed};
use pyo3::{PyResult, Python};
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

pub struct Runner<'a> {
    pub mode: Mode,
    pub configuration: Configuration,
    pub cache: Option<&'a mut Cache>,
}

type TaskResult = (usize, Vec<String>);
pub const SUCCESS: usize = 0;
pub const FAIL: usize = 1;
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
    let code = normalize_newlines(code);
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

fn run_task_impl(
    configuration: &Configuration,
    mode: &Mode,
    path: &Path,
    formatter: Option<&Formatter>,
) -> PyResult<(usize, Vec<String>)> {
    let (before, after, newlines_style, unknown_command_warnings) = format_file(path, formatter)?;
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
                rewrite_in_place(path, &before, &after, &newlines_style, warnings)?
            }
            Mode::CheckFormatting => check_formatting(path, &before, &after, warnings),
            Mode::ShowDiff => {
                show_diff(path, configuration.control.color, &before, &after, warnings)?
            }
            Mode::CheckFormattingAndShowDiff => {
                check_and_show_diff(path, configuration.control.color, &before, &after, warnings)?
            }
            _ => do_nothing(),
        }
    };

    Ok((code, warnings))
}

fn run_task(
    configuration: &Configuration,
    mode: &Mode,
    path: &Path,
    formatter: Option<&Formatter>,
) -> (usize, Vec<String>) {
    match run_task_impl(configuration, mode, path, formatter) {
        Ok(ok) => ok,
        Err(err) => {
            let warning = format!(
                "{}: {}",
                path.to_str().unwrap_or("---"),
                Python::attach(|py| err.value(py).to_string())
            );
            (INTERNAL_ERROR, vec![warning])
        }
    }
}

impl Runner<'_> {
    pub fn handle_already_formatted_files(&mut self, files: &[PathBuf]) -> Vec<usize> {
        files
            .iter()
            .map(|f| {
                let (code, warnings) = run_task(&self.configuration, &self.mode, f, None);
                for warning in warnings {
                    warn(warning);
                }
                code
            })
            .collect()
    }

    fn should_cache(&self) -> bool {
        self.cache.is_some()
            && matches!(
                self.mode,
                Mode::CheckFormatting | Mode::CheckFormattingAndShowDiff | Mode::RewriteInPlace
            )
    }

    pub fn handle_files_to_format(&mut self, files: Vec<PathBuf>) -> PyResult<Vec<usize>> {
        let configuration_summary = self.configuration.outcome.summarize()?;
        let formatter = Formatter::new(self.configuration.clone())?;
        let formatter = Some(&formatter);

        let should_cache = self.should_cache();
        let mut result = Vec::<usize>::new();
        let mut files_to_cache = Vec::<PathBuf>::new();

        for f in files {
            let (code, warnings) = run_task(&self.configuration, &self.mode, &f, formatter);
            result.push(code);

            let has_warnings = if self.configuration.outcome.warn_about_unknown_commands {
                !warnings.is_empty()
            } else {
                false
            };

            if should_cache && (code == SUCCESS) && (!is_stdin(&f)) && (!has_warnings) {
                files_to_cache.push(f);
            }

            for warning in warnings {
                warn(warning);
            }
        }

        if let Some(cache) = &self.cache {
            cache.store_files(&configuration_summary, &files_to_cache);
        }
        Ok(result)
    }
}
