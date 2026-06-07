use pyo3::sync::PyOnceLock;
use pyo3::types::{PyAnyMethods, PyType};
use pyo3::{Bound, FromPyObject, IntoPyObject, Py, PyAny, PyErr, Python};

#[derive(Clone, FromPyObject)]
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

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct Position {
    pub line: usize,
    pub column: usize,
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum Argument {
    Bracket {
        start: String,
        value: String,
        end: String,
        position: Option<Position>,
    },
    Complex {
        arguments: ArgumentsNode,
    },
    Quoted {
        value: String,
        position: Option<Position>,
    },
    Unquoted {
        value: String,
        position: Option<Position>,
    },
}

pub type Arguments = Vec<Argument>;

impl Argument {
    pub fn into_node(self) -> Node {
        match self {
            Self::Bracket {
                start,
                value,
                end,
                position,
            } => Node::Tree {
                data: "bracket_argument".to_string(),
                children: vec![Node::Token {
                    type_: "BRACKET_ARGUMENT".to_string(),
                    value: format!("{start}{value}{end}"),
                    line: position.as_ref().map(|x| x.line),
                    column: position.map(|x| x.column),
                }],
            },
            Self::Complex { arguments } => Node::Tree {
                data: "complex_argument".to_string(),
                children: vec![Node::Tree {
                    data: "arguments".to_string(),
                    children: arguments
                        .into_iter()
                        .map(ArgumentsAtom::into_node)
                        .collect(),
                }],
            },
            Self::Quoted { value, position } => Node::Tree {
                data: "quoted_argument".to_string(),
                children: vec![Node::Token {
                    type_: "QUOTED_ARGUMENT".to_string(),
                    value: format!("\"{value}\""),
                    line: position.as_ref().map(|x| x.line),
                    column: position.map(|x| x.column),
                }],
            },
            Self::Unquoted { value, position } => Node::Tree {
                data: "unquoted_argument".to_string(),
                children: vec![Node::Token {
                    type_: "UNQUOTED_ARGUMENT".to_string(),
                    value,
                    line: position.as_ref().map(|x| x.line),
                    column: position.map(|x| x.column),
                }],
            },
        }
    }
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum CommentedArgumentComment {
    BracketComment(BracketComment),
    LineComment {
        comment: LineComment,
        newline: String,
    },
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum ArgumentsAtom {
    CommentedArgument {
        argument: Argument,
        comment: CommentedArgumentComment,
    },
    Argument(Argument),
    BracketComment(BracketComment),
    LineComment(LineComment),
}

impl ArgumentsAtom {
    pub fn into_node(self) -> Node {
        match self {
            Self::CommentedArgument { argument, comment } => Node::Tree {
                data: "commented_argument".to_string(),
                children: {
                    let mut nodes = vec![argument.into_node()];
                    match comment {
                        CommentedArgumentComment::BracketComment(comment) => {
                            nodes.push(comment.into_node());
                        }
                        CommentedArgumentComment::LineComment { comment, newline } => {
                            nodes.push(comment.into_node());
                            nodes.push(Node::Token {
                                type_: "NEWLINE".to_string(),
                                value: newline,
                                line: None,
                                column: None,
                            });
                        }
                    }
                    nodes
                },
            },
            Self::Argument(argument) => argument.into_node(),
            Self::BracketComment(node) => node.into_node(),
            Self::LineComment(node) => node.into_node(),
        }
    }
}

pub type ArgumentsNode = Vec<ArgumentsAtom>;

#[derive(Eq, Ord, PartialEq, PartialOrd)]
pub enum CommandInvocation {
    KnownCommand {
        identifier: String,
        arguments: ArgumentsNode,
    },
    CustomCommand {
        indentation: String,
        identifier: String,
        arguments: ArgumentsNode,
        formatted_node: String,
        line: usize,
        column: usize,
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
                children: vec![
                    Node::Token {
                        type_: "IDENTIFIER".to_string(),
                        value: identifier,
                        line: None,
                        column: None,
                    },
                    Node::Tree {
                        data: "arguments".to_string(),
                        children: arguments
                            .into_iter()
                            .map(ArgumentsAtom::into_node)
                            .collect(),
                    },
                ],
            },
            Self::CustomCommand {
                indentation,
                identifier,
                arguments,
                formatted_node,
                line,
                column,
            } => Node::Tree {
                data: "custom_command".to_string(),
                children: vec![
                    Node::Token {
                        type_: "ANONYMOUS".to_string(),
                        value: indentation,
                        line: None,
                        column: None,
                    },
                    Node::Token {
                        type_: "IDENTIFIER".to_string(),
                        value: identifier,
                        line: Some(line),
                        column: Some(column),
                    },
                    Node::Tree {
                        data: "arguments".to_string(),
                        children: arguments
                            .into_iter()
                            .map(ArgumentsAtom::into_node)
                            .collect(),
                    },
                    Node::Tree {
                        data: "formatted_node".to_string(),
                        children: vec![Node::Token {
                            type_: "ANONYMOUS".to_string(),
                            value: formatted_node,
                            line: None,
                            column: None,
                        }],
                    },
                ],
            },
        }
    }
}

#[derive(Eq, Ord, PartialEq, PartialOrd)]
pub enum Command {
    Element {
        command_invocation: CommandInvocation,
        line_comment: Option<LineComment>,
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
                    Some(node) => vec![command_invocation.into_node(), node.into_node()],
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

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct BracketComment {
    pub value: String,
}

impl BracketComment {
    pub fn into_node(self) -> Node {
        Node::Tree {
            data: "bracket_comment".to_string(),
            children: vec![
                Node::Token {
                    type_: "POUND_SIGN".to_string(),
                    value: "#".to_string(),
                    line: None,
                    column: None,
                },
                Node::Token {
                    type_: "BRACKET_ARGUMENT".to_string(),
                    value: self.value,
                    line: None,
                    column: None,
                },
            ],
        }
    }
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct LineComment {
    pub value: String,
}

impl LineComment {
    pub fn into_node(self) -> Node {
        Node::Tree {
            data: "line_comment".to_string(),
            children: {
                let pound_sign = Node::Token {
                    type_: "POUND_SIGN".to_string(),
                    value: "#".to_string(),
                    line: None,
                    column: None,
                };
                if self.value.is_empty() {
                    vec![pound_sign]
                } else {
                    vec![
                        pound_sign,
                        Node::Token {
                            type_: "LINE_COMMENT_CONTENT".to_string(),
                            value: self.value,
                            line: None,
                            column: None,
                        },
                    ]
                }
            },
        }
    }
}

#[derive(Eq, Ord, PartialEq, PartialOrd)]
pub enum FileElement {
    Block {
        start: Command,
        body: Vec<FileElement>,
        end: Command,
    },
    Command(Command),
    StandaloneIdentifier {
        value: String,
    },
    NonCommandElement {
        bracket_comments: Vec<BracketComment>,
        line_comment: Option<LineComment>,
    },
    NewlineOrGap {
        value: String,
    },
}

const BLOCK_END: &str = "gersemi: block_end ";
const HINTS: &str = "gersemi: hints";
const IGNORE: &str = "gersemi: ignore";

impl FileElement {
    fn get_standalone_line_comment_content(&self) -> Option<&str> {
        if let Self::NonCommandElement {
            line_comment: Some(LineComment { ref value }),
            ..
        } = self
        {
            Some(value.trim())
        } else {
            None
        }
    }

    pub fn is_ignore_directive(&self) -> bool {
        self.get_standalone_line_comment_content()
            .is_some_and(|value| value.starts_with(IGNORE))
    }

    pub fn get_block_end(&self) -> Option<String> {
        self.get_standalone_line_comment_content()
            .and_then(|value| value.split_once(BLOCK_END))
            .map(|(_, rhs)| rhs.to_string())
    }

    pub fn get_hint(&self) -> Option<String> {
        self.get_standalone_line_comment_content()
            .and_then(|value| value.split_once(HINTS))
            .map(|(_, rhs)| rhs.to_string())
    }

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
                let mut children = bracket_comments
                    .into_iter()
                    .map(BracketComment::into_node)
                    .collect::<Vec<_>>();
                if let Some(node) = line_comment {
                    children.push(node.into_node());
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

impl Start {
    pub fn into_node(self) -> Node {
        Node::Tree {
            data: "start".to_string(),
            children: self
                .children
                .into_iter()
                .map(FileElement::into_node)
                .collect::<Vec<_>>(),
        }
    }
}

impl<'py> IntoPyObject<'py> for Start {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        self.into_node().into_pyobject(py)
    }
}
