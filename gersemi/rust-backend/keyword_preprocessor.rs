use std::collections::HashSet;

use crate::node::{Node, Nodes};

fn get_node_value(node: &Node, case_insensitive: bool) -> String {
    let result = match node {
        Node::Token { value, .. } => value.clone(),
        Node::Tree { data, children } => {
            let result = children
                .iter()
                .map(|child| get_node_value(child, case_insensitive))
                .collect::<String>();
            match data.as_str() {
                "complex_argument" => format!("({result})"),
                _ => result,
            }
        }
    };
    if case_insensitive {
        result.to_lowercase()
    } else {
        result
    }
}

type Bucket = Vec<Node>;

fn get_bucket_value(bucket: &Bucket, case_insensitive: bool) -> (String, Vec<String>) {
    let node = bucket.last().unwrap();
    (
        get_node_value(node, case_insensitive),
        bucket
            .iter()
            .map(|node| get_node_value(node, case_insensitive))
            .collect(),
    )
}

fn bucket_arguments_with_their_preceding_comments(nodes: Nodes) -> Vec<Bucket> {
    let mut result = Vec::<Bucket>::new();
    let mut accumulator = Bucket::new();
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

pub fn keep_unique_arguments(nodes: Nodes) -> Nodes {
    let buckets = bucket_arguments_with_their_preceding_comments(nodes);
    let mut known = HashSet::<(String, Vec<String>)>::new();
    let mut unique_buckets = Vec::<Bucket>::new();
    for bucket in buckets {
        let value = get_bucket_value(&bucket, false);
        if !known.contains(&value) {
            known.insert(value);
            unique_buckets.push(bucket);
        }
    }

    let mut result = Nodes::new();
    for bucket in unique_buckets {
        for node in bucket {
            result.push(node);
        }
    }

    result
}

pub fn sort_arguments(nodes: Nodes, case_insensitive: bool) -> Nodes {
    let mut buckets = bucket_arguments_with_their_preceding_comments(nodes);
    buckets.sort_by_key(|bucket| get_bucket_value(bucket, case_insensitive));

    let mut result = Nodes::new();
    for bucket in buckets {
        for node in bucket {
            result.push(node);
        }
    }

    result
}
