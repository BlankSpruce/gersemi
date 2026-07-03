use crate::configuration::{KeywordFormatter, KeywordPreprocessor};

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct Position {
    pub line: usize,
    pub column: usize,
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct BracketArgument {
    pub bracket_width: usize,
    pub value: String,
    pub position: Option<Position>,
}

impl BracketArgument {
    pub fn flatten(&self) -> String {
        let equal_signs = "=".repeat(self.bracket_width);
        format!("[{equal_signs}[{}]{equal_signs}]", self.value)
    }
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum PhantomKind {
    KeywordPreprocessor(KeywordPreprocessor),
    KeywordFormatter(KeywordFormatter),
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum Argument {
    Bracket(BracketArgument),
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
    Phantom {
        kind: PhantomKind,
        value: String,
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
            Self::Bracket(BracketArgument { value, .. })
            | Self::Quoted { value, .. }
            | Self::Unquoted { value, .. }
            | Self::Phantom { value, .. } => value.clone(),
        }
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub enum CommentedArgumentComment {
    BracketComment(BracketComment),
    LineComment {
        comment: LineComment,
        newline: String,
    },
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
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
}

pub type ArgumentsNode = Vec<ArgumentsAtom>;

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
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

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum Command {
    Element {
        command_invocation: CommandInvocation,
        line_comment: Option<LineComment>,
    },
    Invocation(CommandInvocation),
}

impl Command {
    pub fn command_name(&self) -> &str {
        match self {
            Self::Element {
                command_invocation, ..
            }
            | Self::Invocation(command_invocation) => match command_invocation {
                CommandInvocation::KnownCommand { identifier, .. }
                | CommandInvocation::CustomCommand { identifier, .. } => identifier,
            },
        }
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct BracketComment {
    pub value: String,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct LineComment {
    pub value: String,
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
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
}

#[derive(Clone)]
pub struct Start {
    pub children: Vec<FileElement>,
}

#[derive(Debug, Clone)]
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
    Pair {
        first: Box<RefinedArgumentsAtom>,
        rest: Vec<RefinedArgumentsAtom>,
    },
}

pub type RefinedArgumentsNode = Vec<RefinedArgumentsAtom>;

impl RefinedArgumentsAtom {
    pub fn is_commented_argument(&self) -> bool {
        matches!(
            self,
            RefinedArgumentsAtom::Atom(ArgumentsAtom::CommentedArgument { .. })
        )
    }

    pub fn get_value(&self) -> Option<String> {
        match self {
            Self::Atom(atom) => atom.get_value(),
            _ => None,
        }
    }

    pub fn is_phantom(&self) -> bool {
        match self {
            RefinedArgumentsAtom::Atom(
                ArgumentsAtom::CommentedArgument { argument, .. }
                | ArgumentsAtom::Argument(argument),
            ) => matches!(argument, Argument::Phantom { .. }),
            _ => false,
        }
    }

    pub fn get_phantom_kind(&self) -> Option<PhantomKind> {
        match self {
            RefinedArgumentsAtom::Atom(
                ArgumentsAtom::CommentedArgument {
                    argument: Argument::Phantom { kind, .. },
                    ..
                }
                | ArgumentsAtom::Argument(Argument::Phantom { kind, .. }),
            ) => Some(kind.clone()),
            _ => None,
        }
    }
}
