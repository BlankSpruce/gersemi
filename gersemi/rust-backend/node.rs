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
    pub fn get_value(&self) -> String {
        match self {
            Self::Complex { arguments } => arguments
                .iter()
                .filter_map(|x| match x {
                    ArgumentsAtom::Argument(node)
                    | ArgumentsAtom::CommentedArgument { argument: node, .. } => {
                        Some(node.get_value())
                    }
                    ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
                })
                .collect::<Vec<_>>()
                .join(" "),
            Self::Bracket { value, .. }
            | Self::Quoted { value, .. }
            | Self::Unquoted { value, .. } => value.clone(),
        }
    }

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
    pub fn is_comment(&self) -> bool {
        match self {
            ArgumentsAtom::CommentedArgument { .. } | ArgumentsAtom::Argument(_) => false,
            ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => true,
        }
    }

    pub fn get_value(&self) -> Option<String> {
        match self {
            ArgumentsAtom::CommentedArgument { argument, .. }
            | ArgumentsAtom::Argument(argument) => Some(argument.get_value()),
            ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
        }
    }

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
        position: Position,
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
                position,
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
                        line: Some(position.line),
                        column: Some(position.column),
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

pub struct ConvertFromNode;

impl ConvertFromNode {
    fn block_body(node: &Node) -> Vec<FileElement> {
        let Node::Tree { data, children } = node else {
            return vec![];
        };
        if data != "block_body" {
            return vec![];
        }

        children.iter().map(Self::file_element).collect()
    }

    fn token_value(node: &Node) -> String {
        match node {
            Node::Token { value, .. } => value.clone(),
            Node::Tree { data, children, .. } => Self::token_value(children.first().expect(data)),
        }
    }

    fn token_position(node: &Node) -> Option<Position> {
        match node {
            Node::Token { line, column, .. } => match (*line, *column) {
                (Some(line), Some(column)) => Some(Position { line, column }),
                _ => None,
            },
            Node::Tree { data, children, .. } => {
                Self::token_position(children.first().expect(data))
            }
        }
    }

    fn argument(node: &Node) -> Argument {
        let todo = Argument::Unquoted {
            value: "__TODO_argument__".to_string(),
            position: None,
        };
        let Node::Tree { data, children } = node else {
            return todo;
        };
        match data.as_str() {
            "bracket_argument" => {
                let value = Self::token_value(children.first().expect(data));
                let bracket_length = value[1..].find('[').unwrap_or(0) + 1;

                Argument::Bracket {
                    start: value[..bracket_length].to_string(),
                    value: value[bracket_length..value.len() - bracket_length].to_string(),
                    end: value[value.len() - bracket_length..].to_string(),
                    position: Self::token_position(children.first().expect(data)),
                }
            }
            "complex_argument" => Argument::Complex {
                arguments: Self::arguments(children.first().expect(data)),
            },
            "quoted_argument" => Argument::Quoted {
                value: {
                    let result = Self::token_value(children.first().expect(data));
                    result[1..result.len() - 1].to_string()
                },
                position: Self::token_position(children.first().expect(data)),
            },
            "unquoted_argument" => Argument::Unquoted {
                value: Self::token_value(children.first().expect(data)),
                position: Self::token_position(children.first().expect(data)),
            },
            _ => todo,
        }
    }

    fn bracket_comment(node: &Node) -> BracketComment {
        let todo = BracketComment {
            value: "__TODO_bracket_comment__".to_string(),
        };
        let Node::Tree { data, children } = node else {
            return todo;
        };
        if data != "bracket_comment" {
            return todo;
        }
        BracketComment {
            value: Self::token_value(children.get(1).expect(data)),
        }
    }

    pub fn arguments_atom(node: &Node) -> ArgumentsAtom {
        let todo = ArgumentsAtom::LineComment(Self::line_comment(node));
        let Node::Tree { data, children } = node else {
            return todo;
        };
        match data.as_str() {
            "commented_argument" => ArgumentsAtom::CommentedArgument {
                argument: Self::argument(children.first().expect(data)),
                comment: match children.get(2) {
                    None => CommentedArgumentComment::BracketComment(Self::bracket_comment(
                        children.get(1).expect(data),
                    )),
                    Some(value) => CommentedArgumentComment::LineComment {
                        comment: Self::line_comment(children.get(1).expect(data)),
                        newline: Self::token_value(value),
                    },
                },
            },
            "line_comment" => ArgumentsAtom::LineComment(Self::line_comment(node)),
            "bracket_comment" => ArgumentsAtom::BracketComment(Self::bracket_comment(node)),
            _ => ArgumentsAtom::Argument(Self::argument(node)),
        }
    }

    pub fn refined_arguments(node: &Node) -> RefinedArgumentsNode {
        let Node::Tree { data, children } = node else {
            return vec![];
        };
        if data != "arguments" {
            return vec![];
        }
        children.iter().map(Self::refined_arguments_atom).collect()
    }

    pub fn arguments(node: &Node) -> ArgumentsNode {
        let Node::Tree { data, children } = node else {
            return vec![];
        };
        if data != "arguments" {
            return vec![];
        }
        children.iter().map(Self::arguments_atom).collect()
    }

    pub fn refined_arguments_atom(node: &Node) -> RefinedArgumentsAtom {
        let todo = RefinedArgumentsAtom::Atom(ArgumentsAtom::LineComment(Self::line_comment(node)));
        let Node::Tree { data, children } = node else {
            return todo;
        };
        match data.as_str() {
            "keyword_argument" => RefinedArgumentsAtom::KeywordArgument {
                first: Self::arguments_atom(children.first().expect(data)),
                in_between: children[1..children.len() - 1]
                    .iter()
                    .map(Self::arguments_atom)
                    .collect(),
                second: Self::arguments_atom(children.last().expect(data)),
            },
            _ => RefinedArgumentsAtom::Atom(Self::arguments_atom(node)),
        }
    }

    fn command_invocation(node: &Node) -> CommandInvocation {
        let todo = CommandInvocation::KnownCommand {
            identifier: "__TODO_command_invocation__".to_string(),
            arguments: vec![],
        };

        let Node::Tree { data, children } = node else {
            return todo;
        };
        match data.as_str() {
            "command_invocation" => CommandInvocation::KnownCommand {
                identifier: Self::token_value(children.first().expect(data)),
                arguments: Self::arguments(children.get(1).expect(data)),
            },
            "custom_command" => CommandInvocation::CustomCommand {
                indentation: Self::token_value(children.first().expect(data)),
                identifier: Self::token_value(children.get(1).expect(data)),
                arguments: Self::arguments(children.get(2).expect(data)),
                formatted_node: Self::token_value(children.get(3).expect(data)),
                position: Self::token_position(children.get(1).expect(data)).expect(data),
            },
            _ => todo,
        }
    }

    fn line_comment(node: &Node) -> LineComment {
        let todo = LineComment {
            value: "__TODO_line_comment__".to_string(),
        };
        let Node::Tree { children, .. } = node else {
            return todo;
        };
        LineComment {
            value: match children.get(1) {
                None => String::new(),
                Some(value) => Self::token_value(value),
            },
        }
    }

    fn command(node: &Node) -> Command {
        let todo = Command::Invocation(CommandInvocation::KnownCommand {
            identifier: "__TODO_command__".to_string(),
            arguments: vec![],
        });

        let Node::Tree { data, children } = node else {
            return todo;
        };
        match data.as_str() {
            "command_element" => Command::Element {
                command_invocation: Self::command_invocation(children.first().expect(data)),
                line_comment: children.get(1).map(Self::line_comment),
            },
            "command_invocation" | "custom_command" => {
                Command::Invocation(Self::command_invocation(node))
            }
            _ => todo,
        }
    }

    fn file_element(node: &Node) -> FileElement {
        let todo = FileElement::StandaloneIdentifier {
            value: "__TODO_file_element__".to_string(),
        };

        match node {
            Node::Tree { data, children } => match data.as_str() {
                "block" => FileElement::Block {
                    start: Self::command(children.first().expect(data)),
                    body: Self::block_body(children.get(1).expect(data)),
                    end: Self::command(children.get(2).expect(data)),
                },
                "custom_command" | "command_invocation" | "command_element" => {
                    FileElement::Command(Self::command(node))
                }
                "standalone_identifier" => FileElement::StandaloneIdentifier {
                    value: Self::token_value(children.first().expect(data)),
                },
                "non_command_element" => {
                    let mut bracket_comments: Vec<BracketComment> = children
                        .iter()
                        .take(children.len() - 1)
                        .map(Self::bracket_comment)
                        .collect();
                    let mut line_comment: Option<LineComment> = None;
                    if let Some(node) = children.last() {
                        if let Node::Tree { data, .. } = node {
                            match data.as_str() {
                                "bracket_comment" => {
                                    bracket_comments.push(Self::bracket_comment(node));
                                }
                                "line_comment" => {
                                    line_comment = Some(Self::line_comment(node));
                                }
                                _ => (),
                            }
                        }
                    }
                    FileElement::NonCommandElement {
                        bracket_comments,
                        line_comment,
                    }
                }
                _ => todo,
            },
            Node::Token { type_, value, .. } => match type_.as_str() {
                "NEWLINE" => FileElement::NewlineOrGap {
                    value: value.clone(),
                },
                _ => todo,
            },
        }
    }

    pub fn start(node: &Node) -> Option<Start> {
        let Node::Tree { data, children } = node else {
            return None;
        };
        if data != "start" {
            return None;
        }

        let children: Vec<FileElement> = children.iter().map(Self::file_element).collect();

        Some(Start { children })
    }
}

#[derive(Clone)]
pub enum RefinedArgumentsAtom {
    Atom(ArgumentsAtom),
    BinaryOperation {
        lhs: Box<RefinedArgumentsAtom>,
        operation: Box<RefinedArgumentsAtom>,
        rhs: Box<RefinedArgumentsAtom>,
    },
    UnaryOperation {
        operation: Box<RefinedArgumentsAtom>,
        operand: Option<Box<RefinedArgumentsAtom>>,
    },
    OptionArgument {
        keyword: Box<RefinedArgumentsAtom>,
    },
    OneValueArgument {
        keyword: Box<RefinedArgumentsAtom>,
        arguments: Vec<RefinedArgumentsAtom>,
    },
    MultiValueArgument {
        keyword: Box<RefinedArgumentsAtom>,
        arguments: Vec<RefinedArgumentsAtom>,
    },
    PositionalArguments(Vec<RefinedArgumentsAtom>),
    Section {
        header: Box<RefinedArgumentsAtom>,
        values: Vec<RefinedArgumentsAtom>,
    },
    KeywordArgument {
        first: ArgumentsAtom,
        in_between: Vec<ArgumentsAtom>,
        second: ArgumentsAtom,
    },
}

pub type RefinedArgumentsNode = Vec<RefinedArgumentsAtom>;

impl RefinedArgumentsAtom {
    pub fn into_node(self) -> Node {
        match self {
            Self::Atom(atom) => atom.into_node(),
            Self::BinaryOperation {
                lhs,
                operation,
                rhs,
            } => Node::Tree {
                data: "binary_operation".to_string(),
                children: vec![lhs.into_node(), operation.into_node(), rhs.into_node()],
            },
            Self::UnaryOperation { operation, operand } => Node::Tree {
                data: "unary_operation".to_string(),
                children: match operand {
                    None => vec![operation.into_node()],
                    Some(operand) => vec![operation.into_node(), operand.into_node()],
                },
            },
            Self::OptionArgument { keyword } => Node::Tree {
                data: "option_argument".to_string(),
                children: vec![keyword.into_node()],
            },
            Self::OneValueArgument { keyword, arguments } => Node::Tree {
                data: "one_value_argument".to_string(),
                children: {
                    let mut children: Nodes = vec![keyword.into_node()];
                    children.extend(arguments.into_iter().map(RefinedArgumentsAtom::into_node));
                    children
                },
            },
            Self::MultiValueArgument { keyword, arguments } => Node::Tree {
                data: "multi_value_argument".to_string(),
                children: {
                    let mut children: Nodes = vec![keyword.into_node()];
                    children.extend(arguments.into_iter().map(RefinedArgumentsAtom::into_node));
                    children
                },
            },
            Self::PositionalArguments(arguments) => Node::Tree {
                data: "positional_arguments".to_string(),
                children: arguments
                    .into_iter()
                    .map(RefinedArgumentsAtom::into_node)
                    .collect(),
            },
            Self::Section { header, values } => Node::Tree {
                data: "section".to_string(),
                children: {
                    let mut children: Nodes = vec![header.into_node()];
                    children.extend(values.into_iter().map(RefinedArgumentsAtom::into_node));
                    children
                },
            },
            Self::KeywordArgument {
                first,
                in_between,
                second,
            } => Node::Tree {
                data: "keyword_argument".to_string(),
                children: {
                    let mut result = vec![first.into_node()];
                    result.extend(in_between.into_iter().map(ArgumentsAtom::into_node));
                    result.push(second.into_node());
                    result
                },
            },
        }
    }
}
