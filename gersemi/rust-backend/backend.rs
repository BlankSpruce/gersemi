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
    use crate::configuration::OutcomeConfiguration;
    use crate::custom_command_definition_finder::CustomCommand;
    use crate::formatter::UnknownCommandsUsed;
    use crate::node::Start;
    use crate::parser::{Error, Parser, ParserDefinitions};
    use crate::sanity_checker::check_equivalence;
    use pyo3::pyfunction;
    use std::collections::HashMap;

    #[pyfunction]
    fn parse(text: String, definitions: ParserDefinitions) -> Result<Start, Error> {
        let parser = Parser::new(text, definitions);
        parser.start()
    }

    #[pyfunction]
    fn find_custom_command_definitions(
        text: String,
        definitions: ParserDefinitions,
        filepath: String,
    ) -> HashMap<String, Vec<CustomCommand>> {
        let parser = Parser::new(text, definitions);
        crate::custom_command_definition_finder::find_custom_command_definitions(&parser, filepath)
    }

    #[pyfunction]
    fn check_code_equivalence(
        definitions: ParserDefinitions,
        before: String,
        after: String,
    ) -> Result<bool, Error> {
        let before = Parser::new(before, definitions.clone()).start()?;
        let after = Parser::new(after, definitions).start()?;

        Ok(check_equivalence(before, after))
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn format_code(
        definitions: ParserDefinitions,
        text: String,
        configuration: OutcomeConfiguration,
        command_schemas: CommandSchemas,
    ) -> Result<(String, UnknownCommandsUsed), Error> {
        let node = Parser::new(text, definitions).start()?;
        Ok(crate::formatter::format(
            node,
            &configuration,
            &command_schemas,
        ))
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
