mod argument_schema;
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
    use crate::argument_schema::{isolate_conditions, ArgumentSchema, KeywordMatcher};
    use crate::custom_command_definition_finder::CustomCommand;
    use crate::keyword_preprocessor::{
        keep_unique_arguments, sort_and_keep_unique_arguments, sort_arguments,
    };
    use crate::node::{Node, Nodes, Start};
    use crate::parser::{tree, Error, Parser, ParserDefinitions};
    use crate::sanity_checker::check_equivalence;
    use crate::two_words_keyword_isolator::TwoWordKeywordMatcher;
    use pyo3::pyfunction;
    use std::collections::HashMap;

    #[pyfunction]
    fn parse(text: String, definitions: ParserDefinitions) -> Result<Start, Error> {
        let parser = Parser::new(text, definitions);
        parser.start()
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn dumper_split_arguments(schema: ArgumentSchema, arguments: Nodes) -> Nodes {
        schema.split_arguments_with_sections(arguments)
    }

    #[pyfunction]
    fn condition_syntax_preprocess_arguments(arguments_node: Node) -> Node {
        let Node::Tree { data, children } = arguments_node else {
            return arguments_node;
        };
        Node::Tree {
            data,
            children: isolate_conditions(children),
        }
    }

    #[pyfunction]
    fn isolate_two_words_keywords(
        two_words_keywords: Vec<TwoWordKeywordMatcher>,
        arguments_node: Node,
    ) -> Node {
        let Node::Tree { data, children } = arguments_node else {
            return arguments_node;
        };
        Node::Tree {
            data,
            children: crate::two_words_keyword_isolator::preprocess_arguments(
                two_words_keywords,
                children,
            ),
        }
    }

    #[pyfunction]
    fn pair_arguments(arguments: Nodes) -> Nodes {
        let mut result = Nodes::new();
        let mut accumulator = Nodes::new();
        for argument in arguments {
            if accumulator.is_empty() {
                if argument.is_comment() {
                    result.push(argument);
                } else {
                    accumulator.push(argument);
                }
            } else {
                let is_comment_node = argument.is_comment();
                accumulator.push(argument);
                if !is_comment_node {
                    let accumulator = std::mem::take(&mut accumulator);
                    result.push(tree("pair", accumulator));
                }
            }
        }

        if !accumulator.is_empty() {
            result.push(tree("pair", accumulator));
        }
        result
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn preprocess_keyword_values(
        nodes: Nodes,
        preprocessor: String,
        case_insensitive: bool,
    ) -> Nodes {
        match preprocessor.as_str() {
            "sort" => sort_arguments(nodes, case_insensitive),
            "unique" => keep_unique_arguments(nodes),
            "sort+unique" => sort_and_keep_unique_arguments(nodes, case_insensitive),
            _ => nodes,
        }
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn is_one_of_keywords(matchers: Vec<KeywordMatcher>, node: Node) -> bool {
        crate::argument_schema::is_one_of_keywords(&matchers, &node)
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
    fn safe_indent(s: &str, indent_symbol: &str) -> String {
        crate::formatter::safe_indent(s, indent_symbol)
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
