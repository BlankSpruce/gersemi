use crate::runner::{fromfile, to_stdout, tofile};
use colored::Colorize;
use pyo3::PyResult;
use similar::TextDiff;
use std::path::Path;

fn get_diff(path: &Path, before: &str, after: &str) -> String {
    TextDiff::from_lines(before, after)
        .unified_diff()
        .context_radius(5)
        .header(fromfile(path), tofile(path))
        .to_string()
}

fn colorize_line(line: &str) -> String {
    let result = if line.starts_with("+++") || line.starts_with("---") {
        line.bold().white()
    } else if line.starts_with("@@") {
        line.cyan()
    } else if line.starts_with('+') {
        line.green()
    } else if line.starts_with('-') {
        line.red()
    } else {
        line.normal()
    };
    result.to_string()
}

fn colorize(s: &str) -> String {
    s.split_inclusive('\n')
        .map(colorize_line)
        .collect::<String>()
}

pub fn print_diff(path: &Path, should_colorize: bool, before: &str, after: &str) -> PyResult<()> {
    let result = get_diff(path, before, after);
    let result: String = if should_colorize {
        colorize(&result)
    } else {
        result
    };

    to_stdout(&result)
}
