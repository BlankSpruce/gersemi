mod argument_schema;
mod keyword_preprocessor;
mod node;
mod parser;
mod two_words_keyword_isolator;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::{isolate_conditions, ArgumentSchema, KeywordMatcher};
    use crate::node::{Node, Nodes};
    use crate::parser::{tree, BlockDefinitions, Error, Parser};
    use crate::two_words_keyword_isolator::TwoWordKeywordMatcher;
    use pyo3::pyfunction;

    #[pyfunction]
    fn parse(
        text: String,
        blocks: BlockDefinitions,
        known_commands: Vec<String>,
    ) -> Result<Node, Error> {
        let parser = Parser::new(text, blocks, known_commands);
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
    fn sort_arguments(nodes: Nodes, case_insensitive: bool) -> Nodes {
        crate::keyword_preprocessor::sort_arguments(nodes, case_insensitive)
    }

    #[pyfunction]
    fn keep_unique_arguments(nodes: Nodes) -> Nodes {
        crate::keyword_preprocessor::keep_unique_arguments(nodes)
    }

    #[pyfunction]
    fn sort_and_keep_unique_arguments(nodes: Nodes, case_insensitive: bool) -> Nodes {
        crate::keyword_preprocessor::sort_arguments(
            crate::keyword_preprocessor::keep_unique_arguments(nodes),
            case_insensitive,
        )
    }

    #[pyfunction]
    #[allow(clippy::needless_pass_by_value)]
    fn is_one_of_keywords(matchers: Vec<KeywordMatcher>, node: Node) -> bool {
        crate::argument_schema::is_one_of_keywords(&matchers, &node)
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
