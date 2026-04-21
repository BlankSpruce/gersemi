use pyo3::FromPyObject;

#[derive(FromPyObject)]
pub enum Node {
    Tree {
        data: String,
        children: Nodes,
    },
    Token {
        #[pyo3(attribute("type"))]
        type_: String,

        value: String,
        line: Option<usize>,
        column: Option<usize>,
    },
}

pub type Nodes = Vec<Node>;

impl Node {
    pub fn is_comment(&self) -> bool {
        match self {
            Node::Token { .. } => false,
            Node::Tree { data, .. } => data == "bracket_comment" || data == "line_comment",
        }
    }
}
