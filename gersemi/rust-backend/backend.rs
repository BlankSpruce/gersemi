mod argument_schema;
mod node;
mod parser;
mod two_words_keyword_isolator;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::argument_schema::{isolate_conditions, ArgumentSchema};
    use crate::node::{Node, Nodes};
    use crate::parser::{BlockDefinitions, Error, Parser};
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
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
