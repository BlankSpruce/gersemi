use crate::node::{Node, Nodes};
use crate::parser::tree;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyTuple};
use pyo3::{FromPyObject, PyAny};
use std::cmp::min;
use std::collections::HashMap;

#[derive(Eq, Hash, PartialEq)]
pub enum SecondKeyword {
    String(String),
    Any,
}

#[derive(Eq, Hash, PartialEq)]
struct KeywordMatcher {
    first: String,
    second: Option<SecondKeyword>,
}

fn single_word_matcher(s: &str) -> KeywordMatcher {
    KeywordMatcher {
        first: s.to_string(),
        second: None,
    }
}

#[derive(FromPyObject)]
pub struct ArgumentSchema {
    options: Vec<KeywordMatcher>,
    one_value_keywords: Vec<KeywordMatcher>,
    multi_value_keywords: Vec<KeywordMatcher>,
    front_positional_arguments: Vec<String>,
    back_positional_arguments: Vec<String>,

    #[pyo3(default)]
    sections: HashMap<KeywordMatcher, ArgumentSchema>,
}

impl FromPyObject<'_, '_> for KeywordMatcher {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let (first, second) = if obj.is_instance_of::<PyString>() {
            (obj.cast::<PyString>()?.str()?.to_string(), None)
        } else if obj.is_instance_of::<PyTuple>() {
            let (left, right) = (obj.get_item(0)?, obj.get_item(1)?);

            let left = left.cast::<PyString>()?.str()?.to_string();
            let right = Some(if right.is_instance_of::<PyString>() {
                SecondKeyword::String(right.cast::<PyString>()?.str()?.to_string())
            } else {
                SecondKeyword::Any
            });

            (left, right)
        } else {
            return Err(PyRuntimeError::new_err("Invalid keyword matcher"));
        };

        Ok(KeywordMatcher { first, second })
    }
}

pub fn is_keyword(matcher: &String, data: &str, children: &[Node]) -> bool {
    if children.is_empty() {
        return false;
    }

    match data {
        "commented_argument" => match &children[0] {
            Node::Token { .. } => false,
            Node::Tree { data, children } => is_keyword(matcher, data, children),
        },
        _ => match &children[0] {
            Node::Token { value, .. } => value == matcher,
            Node::Tree { .. } => false,
        },
    }
}

fn matches_second(matcher: &SecondKeyword, data: &str, children: &[Node]) -> bool {
    match matcher {
        SecondKeyword::Any => true,
        SecondKeyword::String(matcher) => is_keyword(matcher, data, children),
    }
}

impl KeywordMatcher {
    fn matches(&self, node: &Node) -> bool {
        let Node::Tree { data, children } = node else {
            return false;
        };

        let Some(second) = &self.second else {
            return is_keyword(&self.first, data, children);
        };

        if data != "keyword_argument" {
            return false;
        }

        match &children[0] {
            Node::Tree {
                data: first_data,
                children: first_children,
            } => {
                if !is_keyword(&self.first, first_data, first_children) {
                    return false;
                }

                match &children[1] {
                    Node::Tree {
                        data: second_data,
                        children: second_children,
                    } => matches_second(second, second_data, second_children),
                    Node::Token { .. } => false,
                }
            }
            Node::Token { .. } => false,
        }
    }
}

enum AccumulatorKind {
    Nodes,
    PositionalArguments,
}

struct Accumulator {
    kind: AccumulatorKind,
    nodes: Nodes,
}

struct KeywordSplitter {
    groups: Nodes,
    accumulator: Accumulator,
    comment_accumulator: Nodes,
}

impl KeywordSplitter {
    fn flush_accumulators(&mut self) {
        let nodes = std::mem::take(&mut self.accumulator.nodes);
        if !nodes.is_empty() {
            self.groups.push(tree(
                match self.accumulator.kind {
                    AccumulatorKind::PositionalArguments => "positional_arguments",
                    AccumulatorKind::Nodes => "multi_value_argument",
                },
                nodes,
            ));
        }
        self.groups.append(&mut self.comment_accumulator);
    }

    fn split(&mut self, schema: &ArgumentSchema, arguments: Nodes) {
        let mut iterator = arguments.into_iter();

        while let Some(argument) = iterator.next() {
            if argument.is_comment() {
                self.comment_accumulator.push(argument);
            } else if schema.is_one_of_options(&argument) {
                self.flush_accumulators();
                self.groups.push(tree("option_argument", vec![argument]));
            } else if schema.is_one_of_one_value_keywords(&argument) {
                self.flush_accumulators();
                let mut group = vec![argument];
                for n in iterator.by_ref() {
                    let stop = !n.is_comment();
                    group.push(n);
                    if stop {
                        break;
                    }
                }
                self.groups.push(tree("one_value_argument", group));
            } else if schema.is_one_of_multi_value_keywords(&argument) {
                self.flush_accumulators();
                self.accumulator.kind = AccumulatorKind::Nodes;
                self.accumulator.nodes = vec![argument];
            } else if !self.accumulator.nodes.is_empty() {
                self.accumulator.nodes.append(&mut self.comment_accumulator);
                self.accumulator.nodes.push(argument);
            } else {
                if let AccumulatorKind::PositionalArguments = self.accumulator.kind {
                } else {
                    self.accumulator.kind = AccumulatorKind::PositionalArguments;
                }
                self.accumulator.nodes.append(&mut self.comment_accumulator);
                self.accumulator.nodes.push(argument);
            }
        }

        self.flush_accumulators();
    }
}

fn is_among_section_keywords(section_schema: Option<&ArgumentSchema>, argument: &Node) -> bool {
    match section_schema {
        None => false,
        Some(section_schema) => match argument {
            Node::Token { .. } => false,
            Node::Tree { children, .. } => section_schema.is_one_of_schema_keywords(&children[0]),
        },
    }
}

fn is_one_of_keywords(matchers: &[KeywordMatcher], node: &Node) -> bool {
    for matcher in matchers {
        if matcher.matches(node) {
            return true;
        }
    }
    false
}

impl ArgumentSchema {
    fn is_one_of_options(&self, node: &Node) -> bool {
        is_one_of_keywords(&self.options, node)
    }

    fn is_one_of_one_value_keywords(&self, node: &Node) -> bool {
        is_one_of_keywords(&self.one_value_keywords, node)
    }

    fn is_one_of_multi_value_keywords(&self, node: &Node) -> bool {
        is_one_of_keywords(&self.multi_value_keywords, node)
    }

    fn is_one_of_schema_keywords(&self, node: &Node) -> bool {
        self.is_one_of_options(node)
            || self.is_one_of_one_value_keywords(node)
            || self.is_one_of_multi_value_keywords(node)
    }

    fn find_pivot(&self, arguments: &[Node]) -> Option<usize> {
        for (index, argument) in arguments.iter().enumerate() {
            if self.is_one_of_schema_keywords(argument) {
                return Some(index);
            }
        }
        None
    }

    fn separate_front(&self, mut arguments: Nodes) -> (Nodes, Nodes) {
        match self.find_pivot(&arguments) {
            None => (arguments, vec![]),
            Some(pivot) => {
                let tail = arguments.split_off(pivot);
                (arguments, tail)
            }
        }
    }

    fn split_positional_arguments(&self, mut arguments: Nodes) -> Nodes {
        let last_index = min(arguments.len(), self.front_positional_arguments.len());
        let rest = arguments.split_off(last_index);
        let mut arguments = arguments
            .into_iter()
            .map(|argument| tree("positional_arguments", vec![argument]))
            .collect::<Vec<_>>();

        if !rest.is_empty() {
            arguments.push(tree("positional_arguments", rest));
        }

        arguments
    }

    fn split_by_keywords(&self, arguments: Nodes) -> Nodes {
        let mut keyword_splitter = KeywordSplitter {
            groups: vec![],
            accumulator: Accumulator {
                kind: AccumulatorKind::Nodes,
                nodes: vec![],
            },
            comment_accumulator: vec![],
        };
        keyword_splitter.split(self, arguments);
        keyword_splitter.groups
    }

    fn split_arguments(&self, mut arguments: Nodes) -> Nodes {
        let back = if self.back_positional_arguments.len() > arguments.len() {
            vec![]
        } else {
            let index = arguments.len() - self.back_positional_arguments.len();
            arguments.split_off(index)
        };
        let (front, tail) = self.separate_front(arguments);
        let front = self.split_positional_arguments(front);
        let keyworded_arguments = self.split_by_keywords(tail);

        front
            .into_iter()
            .chain(keyworded_arguments)
            .chain(back)
            .collect::<Nodes>()
    }

    fn get_section_schema(&self, node: &Node) -> Option<&ArgumentSchema> {
        for (item, schema) in &self.sections {
            if item.matches(node) {
                return Some(schema);
            }
        }
        None
    }

    fn split_multi_value_argument(&self, data: String, children: Nodes) -> Node {
        let first_node = children.first();
        let Some(first_node) = first_node else {
            return Node::Tree { data, children };
        };

        let Some(section_schema) = self.get_section_schema(first_node) else {
            return Node::Tree { data, children };
        };

        let mut result = children;
        let rest = result.split_off(1);
        let rest = section_schema.split_arguments_with_sections(rest);
        for argument in rest {
            match argument {
                Node::Token { .. } => result.push(argument),
                Node::Tree { data, mut children } => match data.as_str() {
                    "positional_arguments" => result.append(&mut children),
                    _ => result.push(Node::Tree { data, children }),
                },
            }
        }

        tree("section", result)
    }

    fn fix_back_positional_arguments(&self, data: &str, section_children: &mut Nodes) {
        if data != "section" {
            return;
        }

        let pivot = self.back_positional_arguments.len();
        if pivot == 0 {
            return;
        }

        let last = section_children.last_mut();
        let Some(Node::Tree {
            data,
            children: last_children,
        }) = last
        else {
            return;
        };

        match data.as_str() {
            "one_value_argument" | "multi_value_argument" => {
                let last_rest = last_children.split_off(1);

                let mut left_in_place = last_rest;
                let back_positional_arguments =
                    left_in_place.split_off(left_in_place.len() - pivot);
                last_children.append(&mut left_in_place);

                section_children.push(tree("positional_arguments", back_positional_arguments));
            }
            _ => (),
        }
    }

    fn form_sections(&self, arguments: Nodes) -> Nodes {
        let mut result = Nodes::new();
        let mut section_schema: Option<&ArgumentSchema> = None;

        for argument in arguments {
            if is_among_section_keywords(section_schema, &argument) {
                let last = result.last_mut();
                if let Some(Node::Tree { children, .. }) = last {
                    children.push(argument);
                }
            } else {
                if let Some(section_schema) = section_schema {
                    if let Some(Node::Tree { data, children }) = result.last_mut() {
                        section_schema.fix_back_positional_arguments(data, children);
                    }
                }

                section_schema = if let Node::Tree { children, .. } = &argument {
                    if let Some(first) = children.first() {
                        self.get_section_schema(first)
                    } else {
                        None
                    }
                } else {
                    None
                };

                result.push(argument);
            }
        }

        result
    }

    pub fn split_arguments_with_sections(&self, arguments: Nodes) -> Nodes {
        let arguments = self.split_arguments(arguments);
        let preprocessed = arguments
            .into_iter()
            .map(|argument| match argument {
                Node::Token { .. } => argument,
                Node::Tree { data, children } => match data.as_str() {
                    "multi_value_argument" => self.split_multi_value_argument(data, children),
                    _ => Node::Tree { data, children },
                },
            })
            .collect();
        self.form_sections(preprocessed)
    }
}

fn isolate_unary_operators(operators: &[KeywordMatcher], arguments: Nodes) -> Nodes {
    let mut one_behind: Option<Node> = None;
    let mut result = Nodes::new();
    for current in arguments {
        match one_behind {
            None => {
                one_behind = Some(current);
            }
            Some(one_behind_node) => {
                if is_one_of_keywords(operators, &one_behind_node) {
                    if current.is_comment() {
                        result.push(tree("unary_operation", vec![one_behind_node]));
                        result.push(current);
                    } else {
                        result.push(tree("unary_operation", vec![one_behind_node, current]));
                    }
                    one_behind = None;
                } else {
                    result.push(one_behind_node);
                    one_behind = Some(current);
                }
            }
        }
    }

    if let Some(node) = one_behind {
        result.push(node);
    }

    result
}

fn isolate_binary_tests(operators: &[KeywordMatcher], arguments: Nodes) -> Nodes {
    let mut two_behind: Option<Node> = None;
    let mut one_behind: Option<Node> = None;
    let mut result = Nodes::new();

    for current in arguments {
        match (two_behind, one_behind) {
            (None, one_behind_node) => {
                two_behind = one_behind_node;
                one_behind = Some(current);
            }
            (Some(two_behind_node), Some(one_behind_node)) => {
                if is_one_of_keywords(operators, &one_behind_node) {
                    result.push(tree(
                        "binary_operation",
                        vec![two_behind_node, one_behind_node, current],
                    ));
                    two_behind = None;
                    one_behind = None;
                } else {
                    result.push(two_behind_node);
                    two_behind = Some(one_behind_node);
                    one_behind = Some(current);
                }
            }
            (Some(two_behind_node), None) => {
                result.push(two_behind_node);
                two_behind = None;
                one_behind = Some(current);
            }
        }
    }

    if let Some(node) = two_behind {
        result.push(node);
    }

    if let Some(node) = one_behind {
        result.push(node);
    }

    result
}

pub fn isolate_conditions(arguments: Nodes) -> Nodes {
    let unary_operators = [
        "COMMAND",
        "POLICY",
        "TARGET",
        "TEST",
        "EXISTS",
        "IS_DIRECTORY",
        "IS_SYMLINK",
        "IS_ABSOLUTE",
        "DEFINED",
        "IS_READABLE",
        "IS_WRITABLE",
        "IS_EXECUTABLE",
    ]
    .map(single_word_matcher);
    let binary_operators = [
        "IS_NEWER_THAN",
        "MATCHES",
        "LESS",
        "GREATER",
        "EQUAL",
        "LESS_EQUAL",
        "GREATER_EQUAL",
        "STRLESS",
        "STRGREATER",
        "STREQUAL",
        "STRLESS_EQUAL",
        "STRGREATER_EQUAL",
        "VERSION_LESS",
        "VERSION_GREATER",
        "VERSION_EQUAL",
        "VERSION_LESS_EQUAL",
        "VERSION_GREATER_EQUAL",
        "IN_LIST",
        "PATH_EQUAL",
    ]
    .map(single_word_matcher);
    let not_operator = [single_word_matcher("NOT")];
    let and_operator = [single_word_matcher("AND")];
    let or_operator = [single_word_matcher("OR")];

    isolate_unary_operators(
        &or_operator,
        isolate_unary_operators(
            &and_operator,
            isolate_unary_operators(
                &not_operator,
                isolate_binary_tests(
                    &binary_operators,
                    isolate_unary_operators(&unary_operators, arguments),
                ),
            ),
        ),
    )
}
