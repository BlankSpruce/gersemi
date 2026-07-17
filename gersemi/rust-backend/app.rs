use crate::args::Args;
use crate::args::Mode;
use crate::cache::file_entry;
use crate::cache::Cache;
use crate::configuration::{Configuration, ControlConfiguration, OutcomeConfiguration};
use crate::gersemi_rust_backend::get_files;
use crate::runner::is_stdin;
use crate::runner::{Runner, FAIL, SUCCESS};
use crate::utils::find_closest_dot_gersemirc;
use crate::utils::print_configuration_report;
use crate::utils::{make_control_configuration, make_outcome_configuration};
use crate::warning_sink::{flush_warnings, register_warning_sink, WarningSink};
use pyo3::exceptions::PyRuntimeError;
use pyo3::{pyclass, pymethods, Py, PyAny, PyResult};
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
    cache: Cache,
    configuration: ControlConfiguration,
    args: Args,
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

pub type Buckets = Vec<(Option<PathBuf>, Vec<PathBuf>)>;

fn has_stdin_mixed_with_files(paths: &[PathBuf]) -> bool {
    let number_of_stdin_paths = paths.iter().filter(|x| is_stdin(x)).count();
    (number_of_stdin_paths > 0) && (number_of_stdin_paths != paths.len())
}

#[pymethods]
impl App {
    #[new]
    #[allow(clippy::needless_pass_by_value)]
    fn new(args: Py<PyAny>) -> PyResult<Self> {
        let configuration = make_control_configuration(&args)?;
        register_warning_sink(WarningSink::new(configuration.quiet));
        let cache = Cache::new(
            configuration.cache && configuration.line_ranges.is_empty(),
            &configuration.cache_dir,
        );
        Ok(Self {
            cache,
            configuration,
            args: Args::new(args)?,
            status_code: StatusCode::new(),
        })
    }

    #[allow(clippy::needless_pass_by_value)]
    fn handle_files(
        &mut self,
        configuration_file: Option<PathBuf>,
        files: Vec<PathBuf>,
    ) -> PyResult<()> {
        let outcome = make_outcome_configuration(configuration_file.as_ref(), &self.args.obj)?;
        if outcome.disable_formatting {
            return Ok(());
        }

        let configuration = Configuration {
            control: self.configuration.clone(),
            outcome,
        };
        let (already_formatted_files, files_to_format) =
            split_files_by_formatting_state(&mut self.cache, files, &configuration.outcome)?;
        let mut runner = Runner {
            mode: self.args.mode.clone(),
            configuration,
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
        let has_warnings = flush_warnings();
        self.status_code
            .add(if self.configuration.warnings_as_errors && has_warnings {
                FAIL
            } else {
                SUCCESS
            });
    }

    fn status_code(&self) -> usize {
        self.status_code.value
    }

    fn get_source_file_buckets(&self) -> PyResult<Buckets> {
        let sources = get_files(
            self.args.sources.clone(),
            self.configuration.respect_ignore_files,
        )?;
        if (!self.configuration.line_ranges.is_empty()) && (sources.len() > 1) {
            return Err(PyRuntimeError::new_err(
                "Line range formatting available only with one source file",
            ));
        }

        if let Some(config_file) = &self.configuration.configuration_file {
            return Ok(vec![(Some(config_file.clone()), sources)]);
        }

        let mut result = Vec::new();
        for source in sources {
            let config_file = find_closest_dot_gersemirc(&source)?;
            match result.iter_mut().find(|(key, _)| *key == config_file) {
                None => result.push((config_file, vec![source])),
                Some((_, values)) => values.push(source),
            }
        }
        Ok(result)
    }

    fn run(&mut self) -> PyResult<usize> {
        if self.args.sources.is_empty() {
            return Ok(self.status_code());
        }

        if has_stdin_mixed_with_files(&self.args.sources) {
            return Err(PyRuntimeError::new_err("Don't mix stdin with file input"));
        }

        if let Some(defs) = &self.args.definitions {
            if has_stdin_mixed_with_files(defs) {
                return Err(PyRuntimeError::new_err("Don't mix stdin with file input"));
            }
        }

        let buckets = self.get_source_file_buckets()?;
        let is_print_config_mode = matches!(self.args.mode, Mode::PrintConfig);
        for (configuration_file, files) in buckets {
            if is_print_config_mode {
                print_configuration_report(configuration_file, files, &self.args.obj)?;
            } else {
                self.handle_files(configuration_file, files)?;
            }
        }

        self.handle_warnings();
        Ok(self.status_code())
    }
}
