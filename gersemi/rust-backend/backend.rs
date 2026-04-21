mod dumper;
mod node;
mod parser;

use pyo3::pymodule;

#[pymodule]
mod gersemi_rust_backend {
    use crate::dumper::Dumper;
    use crate::node::{Node, Nodes};
    use crate::parser::{BlockDefinitions, Error, Parser};
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
    fn argument_aware_split_arguments(dumper: Dumper, arguments: Nodes) -> Nodes {
        dumper.split_arguments(arguments)
    }

    #[pyfunction]
    fn version() -> &'static str {
        static RESULT: &str = env!("CARGO_VERSION");
        RESULT
    }
}
