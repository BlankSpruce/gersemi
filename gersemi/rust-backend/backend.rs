mod argument_schema;
mod cache;
mod configuration;
mod custom_command_definition_finder;
mod diff;
mod formatter;
mod keyword_preprocessor;
mod mode;
mod node;
mod parser;
mod python_side;
mod runner;
mod sanity_checker;
mod two_words_keyword_isolator;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::{CommandSchemaMapping, CommandSchemas};
    use crate::cache::file_entry;
    use crate::configuration::{Configuration, OutcomeConfiguration};
    use crate::custom_command_definition_finder::CustomCommand;
    use crate::mode::Mode;
    use crate::parser::{Error, Parser};
    use crate::runner::{is_stdin, Runner};
    use crate::sanity_checker::check_equivalence;
    use ignore::WalkBuilder;
    use pyo3::exceptions::PyRuntimeError;
    use pyo3::{pyfunction, PyResult};
    use std::collections::HashMap;
    use std::path::PathBuf;

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn validate(text: String, schemas: CommandSchemaMapping) -> Result<(), Error> {
        let schemas = CommandSchemas {
            definition_schemas: schemas,
            extension_schemas: HashMap::new(),
        };
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
    pub fn find_custom_command_definitions(
        text: String,
        filepath: String,
    ) -> PyResult<HashMap<String, Vec<CustomCommand>>> {
        if !has_custom_command_definition(&text) {
            return Ok(HashMap::new());
        }

        let schemas = CommandSchemas {
            definition_schemas: HashMap::new(),
            extension_schemas: HashMap::new(),
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
        let schemas = CommandSchemas {
            definition_schemas: schemas,
            extension_schemas: HashMap::new(),
        };
        let before = Parser::new(before, &schemas).start()?;
        let after = Parser::new(after, &schemas).start()?;

        Ok(check_equivalence(before, after))
    }

    #[pymodule_export]
    use crate::formatter::Formatter;

    #[pymodule_export]
    use crate::cache::Cache;

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    pub fn get_files(paths: Vec<PathBuf>, respect_ignore_files: bool) -> PyResult<Vec<PathBuf>> {
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

    #[pymodule_export]
    use crate::runner::WarningSink;

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn handle_already_formatted_files(
        mode: Mode,
        configuration: Configuration,
        warning_sink: &mut WarningSink,
        already_formatted_files: Vec<PathBuf>,
    ) -> Vec<usize> {
        let mut runner = Runner {
            mode,
            configuration,
            warning_sink: Some(warning_sink),
            cache: None,
        };
        runner.handle_already_formatted_files(&already_formatted_files)
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn handle_files_to_format(
        mode: Mode,
        configuration: Configuration,
        warning_sink: &mut WarningSink,
        files_to_format: Vec<PathBuf>,
        cache: &mut Cache,
    ) -> PyResult<Vec<usize>> {
        let mut runner = Runner {
            mode,
            configuration: configuration.clone(),
            warning_sink: Some(warning_sink),
            cache: Some(cache),
        };
        runner.handle_files_to_format(files_to_format, configuration)
    }

    #[pyfunction]
    fn find_all_custom_command_definitions(
        configuration: Configuration,
        warning_sink: Option<&mut WarningSink>,
    ) -> PyResult<Vec<(String, Vec<CustomCommand>)>> {
        let mut runner = Runner {
            mode: Mode::PrintConfig, // TODO
            configuration,
            warning_sink,
            cache: None,
        };
        runner.find_all_custom_command_definitions()
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn split_files_by_formatting_state(
        cache: &mut Cache,
        files: Vec<PathBuf>,
        configuration: OutcomeConfiguration,
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

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
