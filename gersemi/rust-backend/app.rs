use crate::args::Args;
use crate::args::Mode;
use crate::cache::file_entry;
use crate::cache::Cache;
use crate::configuration::{Configuration, ControlConfiguration, OutcomeConfiguration};
use crate::gersemi_rust_backend::get_files;
use crate::python_side::find_closest_dot_gersemirc;
use crate::runner::{Runner, FAIL, SUCCESS};
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

#[pymethods]
impl App {
    #[new]
    #[allow(clippy::needless_pass_by_value)]
    fn new(configuration: ControlConfiguration, args: Py<PyAny>) -> PyResult<Self> {
        register_warning_sink(WarningSink::new(configuration.quiet));
        let cache = Cache::new(
            configuration.cache && configuration.line_ranges.is_empty(),
            &configuration.cache_dir,
        );
        Ok(Self {
            cache,
            configuration,
            args: Args::new(&args)?,
            status_code: StatusCode::new(),
        })
    }

    fn handle_files(&mut self, configuration: Configuration, files: Vec<PathBuf>) -> PyResult<()> {
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

    fn is_print_config_mode(&self) -> bool {
        matches!(self.args.mode, Mode::PrintConfig)
    }
}
