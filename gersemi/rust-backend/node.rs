use pyo3::sync::PyOnceLock;
use pyo3::types::{PyAnyMethods, PyType};
use pyo3::{Bound, FromPyObject, IntoPyObject, Py, PyAny, PyErr, Python};

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

impl<'py> IntoPyObject<'py> for Node {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        static TREE: PyOnceLock<Py<PyType>> = PyOnceLock::new();
        static TOKEN: PyOnceLock<Py<PyType>> = PyOnceLock::new();
        match self {
            Node::Tree { data, children } => TREE.import(py, "gersemi.types", "Tree")?.call1((
                data,
                children
                    .into_iter()
                    .map(|child| child.into_pyobject(py).unwrap())
                    .collect::<Vec<_>>(),
            )),
            Node::Token {
                type_,
                value,
                line,
                column,
            } => TOKEN
                .import(py, "gersemi.types", "Token")?
                .call1((type_, value, line, column)),
        }
    }
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

pub enum CommandInvocation {
    KnownCommand {
        identifier: Node,
        arguments: Node,
    },
    CustomCommand {
        indentation: Node,
        identifier: Node,
        arguments: Node,
        formatted_node: Node,
    },
}

impl CommandInvocation {
    pub fn into_node(self) -> Node {
        match self {
            Self::KnownCommand {
                identifier,
                arguments,
            } => Node::Tree {
                data: "command_invocation".to_string(),
                children: vec![identifier, arguments],
            },
            Self::CustomCommand {
                indentation,
                identifier,
                arguments,
                formatted_node,
            } => Node::Tree {
                data: "custom_command".to_string(),
                children: vec![indentation, identifier, arguments, formatted_node],
            },
        }
    }
}

pub enum Command {
    Element {
        command_invocation: CommandInvocation,
        line_comment: Option<Node>,
    },
    Invocation(CommandInvocation),
}

impl Command {
    pub fn into_node(self) -> Node {
        match self {
            Self::Element {
                command_invocation,
                line_comment,
            } => {
                let children = match line_comment {
                    None => vec![command_invocation.into_node()],
                    Some(node) => vec![command_invocation.into_node(), node],
                };
                Node::Tree {
                    data: "command_element".to_string(),
                    children,
                }
            }
            Self::Invocation(node) => node.into_node(),
        }
    }
}

pub enum FileElement {
    Block {
        start: Command,
        body: Vec<FileElement>,
        end: Command,
    },
    Command(Command),
    Node(Node),
    StandaloneIdentifier {
        value: String,
    },
    NonCommandElement {
        bracket_comments: Nodes,
        line_comment: Option<Node>,
    },
    NewlineOrGap {
        value: String,
    },
}

impl FileElement {
    pub fn into_node(self) -> Node {
        match self {
            Self::Block { start, body, end } => Node::Tree {
                data: "block".to_string(),
                children: vec![
                    start.into_node(),
                    Node::Tree {
                        data: "block_body".to_string(),
                        children: body.into_iter().map(FileElement::into_node).collect(),
                    },
                    end.into_node(),
                ],
            },
            Self::Command(command) => command.into_node(),
            Self::Node(node) => node,
            Self::StandaloneIdentifier { value } => Node::Tree {
                data: "standalone_identifier".to_string(),
                children: vec![Node::Token {
                    type_: "IDENTIFIER".to_string(),
                    value,
                    line: None,
                    column: None,
                }],
            },
            Self::NonCommandElement {
                bracket_comments,
                line_comment,
            } => {
                let mut children = bracket_comments;
                if let Some(node) = line_comment {
                    children.push(node);
                }
                Node::Tree {
                    data: "non_command_element".to_string(),
                    children,
                }
            }
            Self::NewlineOrGap { value } => Node::Token {
                type_: "NEWLINE".to_string(),
                value,
                line: None,
                column: None,
            },
        }
    }
}

impl<'py> IntoPyObject<'py> for FileElement {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        self.into_node().into_pyobject(py)
    }
}

pub struct Start {
    pub children: Vec<FileElement>,
}

impl<'py> IntoPyObject<'py> for Start {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Node::Tree {
            data: "start".to_string(),
            children: self
                .children
                .into_iter()
                .map(FileElement::into_node)
                .collect::<Vec<_>>(),
        }
        .into_pyobject(py)
    }
}
