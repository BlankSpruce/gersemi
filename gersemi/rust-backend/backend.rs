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
    use crate::parser::{Error, Parser};
    use crate::sanity_checker::check_equivalence;
    use pyo3::pyfunction;
    use pyo3::PyErr;
    use std::collections::HashMap;

    #[pyfunction]
    fn parse(text: String, schemas: CommandSchemas) -> Result<Start, Error> {
        let parser = Parser::new(text, &schemas);
        parser.start()
    }

    #[pyfunction]
    fn find_custom_command_definitions(
        text: String,
        schemas: CommandSchemas,
        filepath: String,
    ) -> HashMap<String, Vec<CustomCommand>> {
        let parser = Parser::new(text, &schemas);
        crate::custom_command_definition_finder::find_custom_command_definitions(&parser, filepath)
    }

    #[pyfunction]
    fn check_code_equivalence(
        schemas: CommandSchemas,
        before: String,
        after: String,
    ) -> Result<bool, Error> {
        let before = Parser::new(before, &schemas).start()?;
        let after = Parser::new(after, &schemas).start()?;

        Ok(check_equivalence(before, after))
    }

    pyo3::import_exception!(gersemi.exceptions, ASTMismatch);

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn format_code(
        text: String,
        configuration: OutcomeConfiguration,
        schemas: CommandSchemas,
    ) -> Result<(String, UnknownCommandsUsed), PyErr> {
        let node = Parser::new(text, &schemas).start()?;
        let before = if configuration.disable_sanity_checks {
            None
        } else {
            Some(node.clone())
        };

        let (result, warnings) = crate::formatter::format(node, &configuration, &schemas);
        if let Some(before) = before {
            let after = Parser::new(result.clone(), &schemas).start()?;
            if !check_equivalence(before, after) {
                return Err(ASTMismatch::new_err(
                    "Reformatting doesn't produce equivalent code.",
                ));
            }
        }
        Ok((result, warnings))
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
