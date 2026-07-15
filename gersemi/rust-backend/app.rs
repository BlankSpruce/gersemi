use crate::cache::file_entry;
use crate::configuration::{Configuration, ControlConfiguration, OutcomeConfiguration};
use crate::runner::{Runner, WarningSink, FAIL, SUCCESS};
use crate::{cache::Cache, mode::Mode};
use pyo3::{pyclass, pymethods, PyResult};
use std::path::PathBuf;

pub struct StatusCode {
    value: usize,
}

impl StatusCode {
    pub fn new() -> Self {
        Self { value: SUCCESS }
    }

    pub fn add(&mut self, value: usize) {
        self.value = self.value.max(value);
    }
}

#[pyclass]
pub struct App {
    mode: Mode,
    cache: Cache,
    warning_sink: WarningSink,
    configuration: ControlConfiguration,
    status_code: StatusCode,
}

fn split_files_by_formatting_state(
    cache: &mut Cache,
    files: Vec<PathBuf>,
    configuration: &OutcomeConfiguration,
) -> PyResult<(Vec<PathBuf>, Vec<PathBuf>)> {
    let mut already_formatted_files = Vec::<PathBuf>::new();
    let mut files_to_format = Vec::<PathBuf>::new();
    let configuration_summary = configuration.summarize()?;
    let known_files = cache.get_files(&configuration_summary);

    for f in files {
        let Some(known_file_metadata) = known_files.get(&f) else {
            files_to_format.push(f);
            continue;
        };

        let Ok((_, size, modification_time)) = file_entry(&f) else {
            files_to_format.push(f);
            continue;
        };
        if (size, modification_time) == *known_file_metadata {
            already_formatted_files.push(f);
        } else {
            files_to_format.push(f);
        }
    }
    Ok((already_formatted_files, files_to_format))
}

#[pymethods]
impl App {
    #[new]
    fn new(mode: Mode, configuration: ControlConfiguration) -> Self {
        let cache = Cache::new(
            configuration.cache && configuration.line_ranges.is_empty(),
            &configuration.cache_dir,
        );
        let warning_sink = WarningSink::new(configuration.quiet);
        Self {
            mode,
            cache,
            warning_sink,
            configuration,
            status_code: StatusCode::new(),
        }
    }

    fn handle_files(&mut self, configuration: Configuration, files: Vec<PathBuf>) -> PyResult<()> {
        let (already_formatted_files, files_to_format) =
            split_files_by_formatting_state(&mut self.cache, files, &configuration.outcome)?;
        let mut runner = Runner {
            mode: self.mode.clone(),
            configuration,
            warning_sink: Some(&mut self.warning_sink),
            cache: Some(&mut self.cache),
        };
        for code in runner.handle_already_formatted_files(&already_formatted_files) {
            self.status_code.add(code);
        }

        for code in runner.handle_files_to_format(files_to_format)? {
            self.status_code.add(code);
        }
        Ok(())
    }

    fn handle_warnings(&mut self) {
        self.status_code.add(
            if self.configuration.warnings_as_errors
                && self.warning_sink.at_least_one_warning_issued
            {
                FAIL
            } else {
                SUCCESS
            },
        );
        self.warning_sink.flush();
    }

    fn status_code(&self) -> usize {
        self.status_code.value
    }

    fn warn(&mut self, s: String) {
        self.warning_sink.__call__(s);
    }
}
