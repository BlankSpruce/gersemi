mod app;
mod args;
mod argument_schema;
mod cache;
mod configuration;
mod custom_command_definition_finder;
mod diff;
mod formatter;
mod keyword_preprocessor;
mod node;
mod parser;
mod runner;
mod sanity_checker;
mod two_words_keyword_isolator;
mod utils;
mod warning_sink;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::CommandSchemas;
    use crate::parser::{Error, Parser};
    use crate::runner::is_stdin;
    use crate::sanity_checker::check_equivalence;
    use ignore::types::{Types, TypesBuilder};
    use ignore::WalkBuilder;
    use pyo3::exceptions::PyRuntimeError;
    use pyo3::{pyfunction, PyResult};
    use std::collections::HashMap;
    use std::path::PathBuf;

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn validate(text: String) -> Result<(), Error> {
        let schemas = CommandSchemas {
            definition_schemas: HashMap::new(),
            extension_schemas: HashMap::new(),
        };
        let parser = Parser::new(text, &schemas);
        parser.start().and(Ok(()))
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn check_code_equivalence(before: String, after: String) -> Result<bool, Error> {
        let schemas = CommandSchemas {
            definition_schemas: HashMap::new(),
            extension_schemas: HashMap::new(),
        };
        let before = Parser::new(before, &schemas).start()?;
        let after = Parser::new(after, &schemas).start()?;

        Ok(check_equivalence(before, after))
    }

    #[pymodule_export]
    use crate::formatter::Formatter;

    #[pymodule_export]
    use crate::app::App;

    fn cmake_types() -> Result<Types, ignore::Error> {
        let mut result = TypesBuilder::new();
        result.add("cmake", "CMakeLists.txt")?;
        result.add("cmake", "*.cmake")?;
        result.add("cmake", "CMakeLists.txt.in")?;
        result.add("cmake", "*.cmake.in")?;
        result.select("cmake");
        let result = result.build();

        if let Err(ref err) = result {
            println!("dbg: {err:?}");
        }

        result
    }

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

        let Ok(type_matcher) = cmake_types() else {
            return fail;
        };

        for entry in builder
            .require_git(false)
            .standard_filters(respect_ignore_files)
            .types(type_matcher)
            .build()
        {
            let Ok(entry) = entry else {
                return fail;
            };

            let p = entry.into_path();
            if p.is_dir() {
                continue;
            }

            result.push(std::path::absolute(p)?);
        }

        result.sort();
        result.dedup();
        Ok(result)
    }

    #[pyfunction]
    pub fn warn(s: String) {
        crate::warning_sink::warn(s);
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }

    #[pyfunction]
    pub fn max_number_of_workers() -> usize {
        match std::thread::available_parallelism() {
            Err(_) => 1,
            Ok(n) => n.get(),
        }
    }
}
