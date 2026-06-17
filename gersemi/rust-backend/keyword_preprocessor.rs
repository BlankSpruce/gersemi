use std::collections::HashSet;

use crate::node::{
    Argument, ArgumentsAtom, BracketComment, CommentedArgumentComment, LineComment,
    RefinedArgumentsAtom, RefinedArgumentsNode,
};

fn get_argument_value(argument: &Argument) -> String {
    match argument {
        Argument::Bracket {
            start, value, end, ..
        } => format!("{start}{value}{end}"),
        Argument::Complex { arguments } => {
            format!(
                "({})",
                arguments.iter().map(get_atom_value).collect::<String>()
            )
        }
        Argument::Quoted { value, .. } => format!("\"{value}\""),
        Argument::Unquoted { value, .. } => value.clone(),
    }
}

fn get_atom_value(atom: &ArgumentsAtom) -> String {
    match atom {
        ArgumentsAtom::CommentedArgument { argument, comment } => {
            let comment_value = match comment {
                CommentedArgumentComment::BracketComment(BracketComment { value })
                | CommentedArgumentComment::LineComment {
                    comment: LineComment { value },
                    ..
                } => value,
            };
            format!("{}{}", get_argument_value(argument), comment_value)
        }
        ArgumentsAtom::Argument(argument) => get_argument_value(argument),
        ArgumentsAtom::BracketComment(BracketComment { value })
        | ArgumentsAtom::LineComment(LineComment { value }) => value.clone(),
    }
}

fn get_node_value(atom: &RefinedArgumentsAtom) -> String {
    let mut result = String::new();
    let mut add = |atom| result.push_str(&get_node_value(atom));
    match atom {
        RefinedArgumentsAtom::Atom(atom) => {
            result.push_str(&get_atom_value(atom));
        }
        RefinedArgumentsAtom::BinaryOperation {
            lhs,
            operation,
            rhs,
        } => {
            add(lhs);
            add(operation);
            add(rhs);
        }
        RefinedArgumentsAtom::UnaryOperation { operation, operand } => {
            add(operation);
            operand.as_deref().map(get_node_value);
        }
        RefinedArgumentsAtom::OptionArgument { keyword } => {
            add(keyword);
        }
        RefinedArgumentsAtom::PositionalArguments(arguments) => {
            for arg in arguments {
                add(arg);
            }
        }
        RefinedArgumentsAtom::KeywordArgument {
            first,
            in_between,
            second,
        } => {
            result.push_str(&get_atom_value(first));
            for arg in in_between {
                result.push_str(&get_atom_value(arg));
            }
            result.push_str(&get_atom_value(second));
        }
        RefinedArgumentsAtom::OneValueArgument {
            keyword: first,
            arguments: rest,
        }
        | RefinedArgumentsAtom::MultiValueArgument {
            keyword: first,
            arguments: rest,
        }
        | RefinedArgumentsAtom::Section {
            header: first,
            values: rest,
        }
        | RefinedArgumentsAtom::Pair { first, rest } => {
            add(first);
            for arg in rest {
                add(arg);
            }
        }
    }

    result
}

type Bucket = Vec<RefinedArgumentsAtom>;

fn get_node_value_impl(atom: &RefinedArgumentsAtom, case_insensitive: bool) -> String {
    let value = get_node_value(atom);
    if case_insensitive {
        value.to_lowercase()
    } else {
        value
    }
}

fn get_bucket_value(bucket: &Bucket, case_insensitive: bool) -> (String, Vec<String>) {
    let node = bucket.last().unwrap();
    (
        get_node_value_impl(node, case_insensitive),
        bucket
            .iter()
            .map(|x| get_node_value_impl(x, case_insensitive))
            .collect(),
    )
}

fn bucket_arguments_with_their_preceding_comments(nodes: RefinedArgumentsNode) -> Vec<Bucket> {
    let mut result = Vec::<Bucket>::new();
    let mut accumulator = RefinedArgumentsNode::new();
    for node in nodes {
        let is_comment_node = node.is_comment();
        accumulator.push(node);
        if !is_comment_node {
            let accumulator = std::mem::take(&mut accumulator);
            result.push(accumulator);
        }
    }

    if !accumulator.is_empty() {
        result.push(accumulator);
    }

    result
}

pub fn keep_unique_arguments(nodes: RefinedArgumentsNode) -> RefinedArgumentsNode {
    let buckets = bucket_arguments_with_their_preceding_comments(nodes);
    let mut known = HashSet::<(String, Vec<String>)>::new();
    let mut unique_buckets = Vec::<Bucket>::new();
    for bucket in buckets {
        let value = get_bucket_value(&bucket, false);
        if known.insert(value) {
            unique_buckets.push(bucket);
        }
    }

    let mut result = RefinedArgumentsNode::new();
    for bucket in unique_buckets {
        for node in bucket {
            result.push(node);
        }
    }

    result
}

pub fn sort_arguments(nodes: RefinedArgumentsNode, case_insensitive: bool) -> RefinedArgumentsNode {
    let mut buckets = bucket_arguments_with_their_preceding_comments(nodes);
    buckets.sort_by_key(|bucket| get_bucket_value(bucket, case_insensitive));

    let mut result = RefinedArgumentsNode::new();
    for bucket in buckets {
        for node in bucket {
            result.push(node);
        }
    }

    result
}

pub fn sort_and_keep_unique_arguments(
    nodes: RefinedArgumentsNode,
    case_insensitive: bool,
) -> RefinedArgumentsNode {
    sort_arguments(keep_unique_arguments(nodes), case_insensitive)
}
