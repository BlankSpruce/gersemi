use crate::node::{Node, Nodes};
use crate::parser::tree;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyTuple};
use pyo3::{FromPyObject, PyAny};
use std::cmp::min;
use std::collections::HashMap;

#[derive(Eq, Hash, PartialEq)]
enum SecondKeyword {
    String(String),
    Any,
}

#[derive(Eq, Hash, PartialEq)]
struct KeywordMatcher {
    first: String,
    second: Option<SecondKeyword>,
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

pub type Dumper = ArgumentSchema;

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

fn is_keyword(matcher: &String, data: &str, children: &[Node]) -> bool {
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
        if let Node::Tree { data, children } = node {
            return match &self.second {
                None => is_keyword(&self.first, data, children),
                Some(second) => {
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
            };
        }

        false
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

    fn split(&mut self, dumper: &Dumper, arguments: Nodes) {
        let mut iterator = arguments.into_iter();

        while let Some(argument) = iterator.next() {
            if argument.is_comment() {
                self.comment_accumulator.push(argument);
            } else if dumper.is_one_of_options(&argument) {
                self.flush_accumulators();
                self.groups.push(tree("option_argument", vec![argument]));
            } else if dumper.is_one_of_one_value_keywords(&argument) {
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
            } else if dumper.is_one_of_multi_value_keywords(&argument) {
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

fn is_among_section_keywords(section_dumper: Option<&ArgumentSchema>, argument: &Node) -> bool {
    match section_dumper {
        None => false,
        Some(section_dumper) => match argument {
            Node::Token { .. } => false,
            Node::Tree { children, .. } => section_dumper.is_one_of_keywords(&children[0]),
        },
    }
}

impl Dumper {
    fn is_one_of_options(&self, node: &Node) -> bool {
        for matcher in &self.options {
            if matcher.matches(node) {
                return true;
            }
        }
        false
    }

    fn is_one_of_one_value_keywords(&self, node: &Node) -> bool {
        for matcher in &self.one_value_keywords {
            if matcher.matches(node) {
                return true;
            }
        }
        false
    }

    fn is_one_of_multi_value_keywords(&self, node: &Node) -> bool {
        for matcher in &self.multi_value_keywords {
            if matcher.matches(node) {
                return true;
            }
        }
        false
    }

    fn is_one_of_keywords(&self, node: &Node) -> bool {
        self.is_one_of_options(node)
            || self.is_one_of_one_value_keywords(node)
            || self.is_one_of_multi_value_keywords(node)
    }

    fn find_pivot(&self, arguments: &[Node]) -> Option<usize> {
        for (index, argument) in arguments.iter().enumerate() {
            if self.is_one_of_keywords(argument) {
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

    fn get_section_dumper(&self, node: &Node) -> Option<&ArgumentSchema> {
        for (item, schema) in &self.sections {
            if item.matches(node) {
                return Some(schema);
            }
        }
        None
    }

    fn split_multi_value_argument(&self, data: String, children: Nodes) -> Node {
        let first_node = children.first();
        match first_node {
            None => Node::Tree { data, children },
            Some(first_node) => match self.get_section_dumper(first_node) {
                None => Node::Tree { data, children },
                Some(section_dumper) => {
                    let mut result = children;
                    let rest = result.split_off(1);
                    let rest = section_dumper.split_arguments_with_sections(rest);
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
            },
        }
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
        let mut section_dumper: Option<&ArgumentSchema> = None;

        for argument in arguments {
            if is_among_section_keywords(section_dumper, &argument) {
                let last = result.last_mut();
                if let Some(Node::Tree { children, .. }) = last {
                    children.push(argument);
                }
            } else {
                if let Some(section_dumper) = section_dumper {
                    if let Some(Node::Tree { data, children }) = result.last_mut() {
                        section_dumper.fix_back_positional_arguments(data, children);
                    }
                }

                if let Node::Tree { children, .. } = &argument {
                    if children.is_empty() {
                        section_dumper = None;
                    } else if let Some(last) = children.first() {
                        section_dumper = self.get_section_dumper(last);
                    } else {
                        section_dumper = None;
                    }
                } else {
                    section_dumper = None;
                }

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
