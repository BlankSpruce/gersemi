use crate::cache::file_entry;
use crate::configuration::{Configuration, ControlConfiguration, OutcomeConfiguration};
use crate::runner::{Runner, WarningSink};
use crate::{cache::Cache, mode::Mode};
use pyo3::{pyclass, pymethods, PyResult};
use std::path::PathBuf;

#[pyclass]
pub struct App {
    mode: Mode,
    cache: Cache,
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
        Self {
            mode,
            cache: Cache::new(
                configuration.cache && configuration.line_ranges.is_empty(),
                configuration.cache_dir,
            ),
        }
    }

    fn handle_files(
        &mut self,
        warning_sink: &mut WarningSink,
        configuration: Configuration,
        files: Vec<PathBuf>,
    ) -> PyResult<Vec<usize>> {
        let (already_formatted_files, files_to_format) =
            split_files_by_formatting_state(&mut self.cache, files, &configuration.outcome)?;
        let mut runner = Runner {
            mode: self.mode.clone(),
            configuration,
            warning_sink: Some(warning_sink),
            cache: Some(&mut self.cache),
        };
        let mut result = runner.handle_already_formatted_files(&already_formatted_files);
        result.extend(runner.handle_files_to_format(files_to_format)?);
        Ok(result)
    }
}
