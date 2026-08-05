use crate::configuration::{KeywordFormatter, KeywordPreprocessor};

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct Position {
    pub line: usize,
    pub column: usize,
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub struct BracketArgument<'a> {
    pub value: &'a str,
    pub whole: &'a str,
    pub position: Option<Position>,
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum InlineHintKind {
    KeywordPreprocessor(KeywordPreprocessor),
    KeywordFormatter(KeywordFormatter),
    AsCommand { command: String },
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum Argument<'a> {
    Bracket(BracketArgument<'a>),
    Complex {
        arguments: ArgumentsNode<'a>,
        as_value: String,
    },
    Quoted {
        value: &'a str,
        position: Option<Position>,
    },
    Unquoted {
        value: &'a str,
        position: Option<Position>,
    },
    InlineHint {
        kind: InlineHintKind,
        value: &'a str,
    },
}

pub type Arguments<'a> = Vec<Argument<'a>>;

impl Argument<'_> {
    pub fn get_value(&self) -> &str {
        match self {
            Self::Complex { as_value, .. } => as_value.as_str(),
            Self::InlineHint { value, .. }
            | Self::Bracket(BracketArgument { value, .. })
            | Self::Quoted { value, .. }
            | Self::Unquoted { value, .. } => value,
        }
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub enum CommentedArgumentComment<'a> {
    BracketComment(BracketComment<'a>),
    LineComment(LineComment<'a>),
}

#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum ArgumentsAtom<'a> {
    CommentedArgument {
        argument: Argument<'a>,
        comment: CommentedArgumentComment<'a>,
    },
    Argument(Argument<'a>),
    BracketComment(BracketComment<'a>),
    LineComment(LineComment<'a>),
}

impl ArgumentsAtom<'_> {
    pub fn is_comment(&self) -> bool {
        match self {
            ArgumentsAtom::CommentedArgument { .. } | ArgumentsAtom::Argument(_) => false,
            ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => true,
        }
    }

    pub fn get_value(&self) -> Option<&str> {
        match self {
            ArgumentsAtom::CommentedArgument { argument, .. }
            | ArgumentsAtom::Argument(argument) => Some(argument.get_value()),
            ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
        }
    }
}

pub type ArgumentsNode<'a> = Vec<ArgumentsAtom<'a>>;

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum CommandInvocation<'a> {
    KnownCommand {
        identifier: String,
        arguments: ArgumentsNode<'a>,
    },
    CustomCommand {
        indentation: String,
        identifier: String,
        arguments: ArgumentsNode<'a>,
        formatted_node: &'a str,
        position: Position,
    },
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum Command<'a> {
    Element {
        command_invocation: CommandInvocation<'a>,
        line_comment: Option<LineComment<'a>>,
    },
    Invocation(CommandInvocation<'a>),
}

impl Command<'_> {
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
pub struct BracketComment<'a> {
    pub value: &'a str,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct LineComment<'a> {
    pub value: &'a str,
}

#[derive(Clone, Eq, Ord, PartialEq, PartialOrd)]
pub enum FileElement<'a> {
    Block {
        start: Command<'a>,
        body: Vec<FileElement<'a>>,
        end: Command<'a>,
    },
    Command(Command<'a>),
    StandaloneIdentifier {
        value: &'a str,
    },
    NonCommandElement {
        bracket_comments: Vec<BracketComment<'a>>,
        line_comment: Option<LineComment<'a>>,
    },
    NewlineOrGap {
        value: &'a str,
    },
}

const BLOCK_END: &str = "gersemi: block_end ";
const HINTS: &str = "gersemi: hints";
const IGNORE: &str = "gersemi: ignore";

impl FileElement<'_> {
    fn get_standalone_line_comment_content(&self) -> Option<&str> {
        if let Self::NonCommandElement {
            line_comment: Some(LineComment { value }),
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
pub struct Start<'a> {
    pub children: Vec<FileElement<'a>>,
}

#[derive(Debug, Clone)]
pub enum RefinedArgumentsAtom<'a> {
    Atom(ArgumentsAtom<'a>),
    BinaryOperation {
        lhs: Box<RefinedArgumentsAtom<'a>>,
        operation: Box<RefinedArgumentsAtom<'a>>,
        rhs: Box<RefinedArgumentsAtom<'a>>,
    },
    UnaryOperation {
        operation: Box<RefinedArgumentsAtom<'a>>,
        operand: Option<Box<RefinedArgumentsAtom<'a>>>,
    },
    OptionArgument {
        keyword: Box<RefinedArgumentsAtom<'a>>,
    },
    OneValueArgument {
        keyword: Box<RefinedArgumentsAtom<'a>>,
        arguments: Vec<RefinedArgumentsAtom<'a>>,
    },
    MultiValueArgument {
        keyword: Box<RefinedArgumentsAtom<'a>>,
        arguments: Vec<RefinedArgumentsAtom<'a>>,
    },
    PositionalArguments(Vec<RefinedArgumentsAtom<'a>>),
    Section {
        header: Box<RefinedArgumentsAtom<'a>>,
        values: Vec<RefinedArgumentsAtom<'a>>,
    },
    KeywordArgument {
        first: ArgumentsAtom<'a>,
        in_between: Vec<ArgumentsAtom<'a>>,
        second: ArgumentsAtom<'a>,
    },
    Pair {
        first: Box<RefinedArgumentsAtom<'a>>,
        rest: Vec<RefinedArgumentsAtom<'a>>,
    },
}

pub type RefinedArgumentsNode<'a> = Vec<RefinedArgumentsAtom<'a>>;

impl RefinedArgumentsAtom<'_> {
    pub fn is_commented_argument(&self) -> bool {
        matches!(
            self,
            RefinedArgumentsAtom::Atom(ArgumentsAtom::CommentedArgument { .. })
        )
    }

    pub fn get_value(&self) -> Option<&str> {
        match self {
            Self::Atom(atom) => atom.get_value(),
            _ => None,
        }
    }

    pub fn is_inline_hint(&self) -> bool {
        match self {
            RefinedArgumentsAtom::Atom(
                ArgumentsAtom::CommentedArgument { argument, .. }
                | ArgumentsAtom::Argument(argument),
            ) => matches!(argument, Argument::InlineHint { .. }),
            _ => false,
        }
    }

    pub fn get_inline_hint_kind(&self) -> Option<InlineHintKind> {
        match self {
            RefinedArgumentsAtom::Atom(
                ArgumentsAtom::CommentedArgument {
                    argument: Argument::InlineHint { kind, .. },
                    ..
                }
                | ArgumentsAtom::Argument(Argument::InlineHint { kind, .. }),
            ) => Some(kind.clone()),
            _ => None,
        }
    }
}
