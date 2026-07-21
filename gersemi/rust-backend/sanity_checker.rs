use crate::node::{
    Argument, ArgumentsAtom, ArgumentsNode, BracketArgument, Command, CommandInvocation,
    CommentedArgumentComment, FileElement, LineComment, Start,
};
use std::collections::BTreeSet;

fn simplify_argument(node: Argument) -> Argument {
    match node {
        Argument::Bracket(BracketArgument {
            bracket_width,
            value,
            ..
        }) => Argument::Bracket(BracketArgument {
            bracket_width,
            value,
            position: None,
        }),
        Argument::Complex { arguments } => Argument::Complex {
            arguments: simplify_arguments(arguments),
        },
        Argument::Quoted { value, .. } => Argument::Quoted {
            value,
            position: None,
        },
        Argument::Unquoted { value, .. } => Argument::Unquoted {
            value,
            position: None,
        },
        Argument::InlineHint { .. } => node,
    }
}

fn simplify_commented_argument_comment(node: CommentedArgumentComment) -> CommentedArgumentComment {
    match node {
        CommentedArgumentComment::BracketComment(_) => node,
        CommentedArgumentComment::LineComment { comment, .. } => {
            CommentedArgumentComment::LineComment {
                comment: simplify_line_comment(comment),
                newline: String::new(),
            }
        }
    }
}

fn simplify_arguments_atom(node: ArgumentsAtom) -> ArgumentsAtom {
    match node {
        ArgumentsAtom::CommentedArgument { argument, comment } => {
            ArgumentsAtom::CommentedArgument {
                argument: simplify_argument(argument),
                comment: simplify_commented_argument_comment(comment),
            }
        }
        ArgumentsAtom::Argument(node) => ArgumentsAtom::Argument(simplify_argument(node)),
        ArgumentsAtom::BracketComment(_) => node,
        ArgumentsAtom::LineComment(node) => ArgumentsAtom::LineComment(simplify_line_comment(node)),
    }
}

fn simplify_arguments(node: ArgumentsNode) -> ArgumentsNode {
    node.into_iter()
        .map(simplify_arguments_atom)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

fn simplify_command_invocation(node: CommandInvocation) -> CommandInvocation {
    match node {
        CommandInvocation::KnownCommand {
            identifier,
            arguments,
        }
        | CommandInvocation::CustomCommand {
            identifier,
            arguments,
            ..
        } => CommandInvocation::KnownCommand {
            identifier: identifier.to_lowercase(),
            arguments: simplify_arguments(arguments),
        },
    }
}

fn simplify_command(node: Command) -> Command {
    match node {
        Command::Element {
            command_invocation: node,
            line_comment,
        } => match line_comment {
            None => Command::Invocation(simplify_command_invocation(node)),
            Some(line_comment) => Command::Element {
                command_invocation: simplify_command_invocation(node),
                line_comment: Some(simplify_line_comment(line_comment)),
            },
        },
        Command::Invocation(node) => Command::Invocation(simplify_command_invocation(node)),
    }
}

fn simplify_line_comment(node: LineComment) -> LineComment {
    let LineComment { value } = node;
    LineComment {
        value: value.trim_end().to_string(),
    }
}

pub fn simplify_file_elements(nodes: Vec<FileElement>) -> Vec<FileElement> {
    let mut result = Vec::<FileElement>::new();
    for node in nodes {
        match node {
            FileElement::Block { start, body, end } => {
                result.push(FileElement::Command(simplify_command(start)));
                result.extend(simplify_file_elements(body));
                result.push(FileElement::Command(simplify_command(end)));
            }
            FileElement::Command(node) => {
                result.push(FileElement::Command(simplify_command(node)));
            }
            FileElement::StandaloneIdentifier { .. } => {
                result.push(node);
            }
            FileElement::NonCommandElement {
                bracket_comments,
                line_comment,
            } => {
                result.push(FileElement::NonCommandElement {
                    bracket_comments,
                    line_comment: line_comment.map(simplify_line_comment),
                });
            }
            FileElement::NewlineOrGap { .. } => (),
        }
    }
    result
}

pub fn check_equivalence(before: Start, after: Start) -> bool {
    let before = simplify_file_elements(before.children);
    let after = simplify_file_elements(after.children);

    before == after
}
