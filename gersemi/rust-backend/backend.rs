mod argument_schema;
mod configuration;
mod custom_command_definition_finder;
mod formatter;
mod keyword_preprocessor;
mod node;
mod parser;
mod sanity_checker;
mod two_words_keyword_isolator;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::CommandSchemas;
    use crate::custom_command_definition_finder::CustomCommand;
    use crate::node::Start;
    use crate::parser::{Error, Parser};
    use crate::sanity_checker::check_equivalence;
    use pyo3::pyfunction;
    use std::collections::HashMap;

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn parse(text: String, schemas: CommandSchemas) -> Result<Start, Error> {
        let parser = Parser::new(text, &schemas);
        parser.start()
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn find_custom_command_definitions(
        text: String,
        schemas: CommandSchemas,
        filepath: String,
    ) -> HashMap<String, Vec<CustomCommand>> {
        let parser = Parser::new(text, &schemas);
        crate::custom_command_definition_finder::find_custom_command_definitions(&parser, filepath)
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn check_code_equivalence(
        schemas: CommandSchemas,
        before: String,
        after: String,
    ) -> Result<bool, Error> {
        let before = Parser::new(before, &schemas).start()?;
        let after = Parser::new(after, &schemas).start()?;

        Ok(check_equivalence(before, after))
    }

    #[pymodule_export]
    use crate::formatter::Formatter;
    
    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
