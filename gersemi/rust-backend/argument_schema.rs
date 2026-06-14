use crate::configuration::{KeywordFormatter, KeywordPreprocessor};
use crate::node::{RefinedArgumentsAtom, RefinedArgumentsNode};
use crate::two_words_keyword_isolator::TwoWordKeywordMatcher;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyTuple};
use pyo3::{FromPyObject, PyAny};
use std::cmp::min;
use std::collections::HashMap;

#[derive(Clone, Eq, Hash, PartialEq)]
pub enum SecondKeyword {
    String(String),
    Any,
}

#[derive(Clone, Eq, Hash, PartialEq)]
pub struct KeywordMatcher {
    first: String,
    second: Option<SecondKeyword>,
}

fn single_word_matcher(s: &str) -> KeywordMatcher {
    KeywordMatcher {
        first: s.to_string(),
        second: None,
    }
}

#[derive(Clone, FromPyObject)]
pub struct ArgumentSchema {
    options: Vec<KeywordMatcher>,
    one_value_keywords: Vec<KeywordMatcher>,
    multi_value_keywords: Vec<KeywordMatcher>,
    front_positional_arguments: Vec<String>,
    back_positional_arguments: Vec<String>,

    #[pyo3(default)]
    sections: HashMap<KeywordMatcher, ArgumentSchema>,

    pub keyword_preprocessors: HashMap<String, KeywordPreprocessor>,
    pub keyword_formatters: HashMap<String, KeywordFormatter>,
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

enum AccumulatorKind {
    Nodes,
    PositionalArguments,
}

struct Accumulator {
    kind: AccumulatorKind,
    nodes: RefinedArgumentsNode,
}

struct KeywordSplitter {
    groups: RefinedArgumentsNode,
    accumulator: Accumulator,
    comment_accumulator: RefinedArgumentsNode,
}

impl KeywordSplitter {
    fn flush_accumulators(&mut self) {
        let mut nodes = std::mem::take(&mut self.accumulator.nodes);
        if !nodes.is_empty() {
            self.groups.push(match self.accumulator.kind {
                AccumulatorKind::PositionalArguments => {
                    RefinedArgumentsAtom::PositionalArguments(nodes)
                }
                AccumulatorKind::Nodes => {
                    let arguments = nodes.split_off(1);
                    RefinedArgumentsAtom::MultiValueArgument {
                        keyword: Box::new(nodes.pop().unwrap()),
                        arguments,
                    }
                }
            });
        }
        self.groups.append(&mut self.comment_accumulator);
    }

    fn split(&mut self, schema: &ArgumentSchema, arguments: RefinedArgumentsNode) {
        let mut iterator = arguments.into_iter();

        while let Some(argument) = iterator.next() {
            if argument.is_comment() {
                self.comment_accumulator.push(argument);
            } else if schema.is_one_of_options(&argument) {
                self.flush_accumulators();
                self.groups.push(RefinedArgumentsAtom::OptionArgument {
                    keyword: Box::new(argument),
                });
            } else if schema.is_one_of_one_value_keywords(&argument) {
                self.flush_accumulators();
                let mut arguments = vec![];
                for n in iterator.by_ref() {
                    let stop = !n.is_comment();
                    arguments.push(n);
                    if stop {
                        break;
                    }
                }
                self.groups.push(RefinedArgumentsAtom::OneValueArgument {
                    keyword: Box::new(argument),
                    arguments,
                });
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

impl ArgumentSchema {
    fn is_one_of_options(&self, node: &RefinedArgumentsAtom) -> bool {
        node.is_one_of_keywords(&self.options)
    }

    fn is_one_of_one_value_keywords(&self, node: &RefinedArgumentsAtom) -> bool {
        node.is_one_of_keywords(&self.one_value_keywords)
    }

    fn is_one_of_multi_value_keywords(&self, node: &RefinedArgumentsAtom) -> bool {
        node.is_one_of_keywords(&self.multi_value_keywords)
    }

    fn is_one_of_schema_keywords(&self, node: &RefinedArgumentsAtom) -> bool {
        self.is_one_of_options(node)
            || self.is_one_of_one_value_keywords(node)
            || self.is_one_of_multi_value_keywords(node)
    }

    fn find_pivot(&self, arguments: &[RefinedArgumentsAtom]) -> Option<usize> {
        for (index, argument) in arguments.iter().enumerate() {
            if self.is_one_of_schema_keywords(argument) {
                return Some(index);
            }
        }
        None
    }

    fn separate_front(
        &self,
        mut arguments: RefinedArgumentsNode,
    ) -> (RefinedArgumentsNode, RefinedArgumentsNode) {
        match self.find_pivot(&arguments) {
            None => (arguments, vec![]),
            Some(pivot) => {
                let tail = arguments.split_off(pivot);
                (arguments, tail)
            }
        }
    }

    fn split_positional_arguments(
        &self,
        mut arguments: RefinedArgumentsNode,
    ) -> RefinedArgumentsNode {
        let last_index = min(arguments.len(), self.front_positional_arguments.len());
        let rest = arguments.split_off(last_index);
        let mut arguments = arguments
            .into_iter()
            .map(|argument| RefinedArgumentsAtom::PositionalArguments(vec![argument]))
            .collect::<Vec<_>>();

        if !rest.is_empty() {
            arguments.push(RefinedArgumentsAtom::PositionalArguments(rest));
        }

        arguments
    }

    fn split_by_keywords(&self, arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
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

    fn split_arguments(&self, mut arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
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
            .collect()
    }

    fn get_section_schema(&self, argument: &RefinedArgumentsAtom) -> Option<&ArgumentSchema> {
        for (item, schema) in &self.sections {
            if argument.is_one_of_keywords(std::slice::from_ref(item)) {
                return Some(schema);
            }
        }
        None
    }

    fn split_multi_value_argument(
        &self,
        keyword: RefinedArgumentsAtom,
        arguments: Vec<RefinedArgumentsAtom>,
    ) -> RefinedArgumentsAtom {
        let Some(section_schema) = self.get_section_schema(&keyword) else {
            return RefinedArgumentsAtom::MultiValueArgument {
                keyword: Box::new(keyword),
                arguments,
            };
        };

        let rest = section_schema.split_arguments_with_sections(arguments);
        let mut values = Vec::<RefinedArgumentsAtom>::new();
        for argument in rest {
            match argument {
                RefinedArgumentsAtom::PositionalArguments(mut arguments) => {
                    values.append(&mut arguments);
                }
                _ => values.push(argument),
            }
        }

        RefinedArgumentsAtom::Section {
            header: Box::new(keyword),
            values,
        }
    }

    fn fix_back_positional_arguments(&self, section_values: &mut Vec<RefinedArgumentsAtom>) {
        let pivot = self.back_positional_arguments.len();
        if pivot == 0 {
            return;
        }

        let last = section_values.last_mut();
        let Some(atom) = last else {
            return;
        };

        match atom {
            RefinedArgumentsAtom::OneValueArgument { arguments, .. }
            | RefinedArgumentsAtom::MultiValueArgument { arguments, .. } => {
                let last_rest = arguments.split_off(1);

                let mut left_in_place = last_rest;
                let back_positional_arguments =
                    left_in_place.split_off(left_in_place.len() - pivot);
                arguments.append(&mut left_in_place);

                section_values.push(RefinedArgumentsAtom::PositionalArguments(
                    back_positional_arguments,
                ));
            }
            _ => (),
        }
    }

    fn form_sections(&self, arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
        let mut result = RefinedArgumentsNode::new();
        let mut section_schema: Option<&ArgumentSchema> = None;

        for argument in arguments {
            if section_schema.is_some_and(|x| x.is_one_of_schema_keywords(&argument)) {
                let last = result.last_mut();
                if let Some(RefinedArgumentsAtom::Section { values, .. }) = last {
                    values.push(argument);
                }
            } else {
                if let Some(section_schema) = section_schema {
                    if let Some(RefinedArgumentsAtom::Section { ref mut values, .. }) =
                        result.last_mut()
                    {
                        section_schema.fix_back_positional_arguments(values);
                    }
                }

                section_schema = self.get_section_schema(&argument);
                result.push(argument);
            }
        }

        result
    }

    pub fn split_arguments_with_sections(
        &self,
        arguments: RefinedArgumentsNode,
    ) -> RefinedArgumentsNode {
        let arguments = self.split_arguments(arguments);
        let preprocessed = arguments
            .into_iter()
            .map(|argument| match argument {
                RefinedArgumentsAtom::MultiValueArgument { keyword, arguments } => {
                    self.split_multi_value_argument(*keyword, arguments)
                }
                _ => argument,
            })
            .collect();
        self.form_sections(preprocessed)
    }
}

impl RefinedArgumentsAtom {
    pub fn is_comment(&self) -> bool {
        match self {
            Self::Atom(atom) => atom.is_comment(),
            Self::BinaryOperation { .. }
            | Self::UnaryOperation { .. }
            | Self::OptionArgument { .. }
            | Self::OneValueArgument { .. }
            | Self::MultiValueArgument { .. }
            | Self::PositionalArguments(_)
            | Self::Section { .. }
            | Self::KeywordArgument { .. }
            | Self::Pair { .. } => false,
        }
    }

    pub fn is_one_of_keywords(&self, matchers: &[KeywordMatcher]) -> bool {
        match self {
            Self::Atom(atom) => match atom.get_value() {
                None => false,
                Some(value) => {
                    for matcher in matchers {
                        if (matcher.first == value) && matcher.second.is_none() {
                            return true;
                        }
                    }
                    false
                }
            },
            Self::KeywordArgument { first, second, .. } => {
                let Some(first_value) = first.get_value() else {
                    return false;
                };
                let second_value = second.get_value();
                for matcher in matchers {
                    if matcher.first != first_value {
                        continue;
                    }

                    match &matcher.second {
                        None | Some(SecondKeyword::Any) => {
                            return true;
                        }
                        Some(SecondKeyword::String(second)) => {
                            if Some(second) == second_value.as_ref() {
                                return true;
                            }
                        }
                    }
                }
                false
            }
            Self::OptionArgument { keyword }
            | Self::OneValueArgument { keyword, .. }
            | Self::MultiValueArgument { keyword, .. }
            | Self::Section {
                header: keyword, ..
            }
            | Self::Pair { first: keyword, .. } => keyword.is_one_of_keywords(matchers),
            Self::BinaryOperation { .. }
            | Self::UnaryOperation { .. }
            | Self::PositionalArguments(_) => false,
        }
    }
}

fn isolate_unary_operators(
    operators: &[KeywordMatcher],
    arguments: RefinedArgumentsNode,
) -> RefinedArgumentsNode {
    let mut one_behind: Option<RefinedArgumentsAtom> = None;
    let mut result = RefinedArgumentsNode::new();
    for current in arguments {
        match one_behind {
            None => {
                one_behind = Some(current);
            }
            Some(one_behind_node) => {
                if one_behind_node.is_one_of_keywords(operators) {
                    if current.is_comment() {
                        result.push(RefinedArgumentsAtom::UnaryOperation {
                            operation: Box::new(one_behind_node),
                            operand: None,
                        });
                        result.push(current);
                    } else {
                        result.push(RefinedArgumentsAtom::UnaryOperation {
                            operation: Box::new(one_behind_node),
                            operand: Some(Box::new(current.clone())),
                        });
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

fn isolate_binary_tests(
    operators: &[KeywordMatcher],
    arguments: RefinedArgumentsNode,
) -> RefinedArgumentsNode {
    let mut two_behind: Option<RefinedArgumentsAtom> = None;
    let mut one_behind: Option<RefinedArgumentsAtom> = None;
    let mut result = RefinedArgumentsNode::new();

    for current in arguments {
        match (two_behind, one_behind) {
            (None, one_behind_node) => {
                two_behind = one_behind_node;
                one_behind = Some(current);
            }
            (Some(two_behind_node), Some(one_behind_node)) => {
                if one_behind_node.is_one_of_keywords(operators) {
                    result.push(RefinedArgumentsAtom::BinaryOperation {
                        lhs: Box::new(two_behind_node),
                        operation: Box::new(one_behind_node),
                        rhs: Box::new(current),
                    });
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

pub fn isolate_conditions(arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
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

pub type Signatures = HashMap<Option<KeywordMatcher>, ArgumentSchema>;

#[allow(clippy::large_enum_variant)]
#[derive(Clone, FromPyObject)]
pub enum CommandSchemaDetails {
    StandardCommand {
        schema: ArgumentSchema,
        signatures: Signatures,
        two_words_keywords: Vec<TwoWordKeywordMatcher>,
    },
    SpecializedCommand {
        #[pyo3(attribute("impl"))]
        specialization: String,
    },
}

#[derive(Clone, FromPyObject)]
pub struct CommandSchema {
    pub block_end: Option<String>,
    pub canonical_name: Option<String>,
    pub inhibit_favour_expansion: bool,
    pub details: CommandSchemaDetails,
}

pub type CommandSchemas = HashMap<String, CommandSchema>;
