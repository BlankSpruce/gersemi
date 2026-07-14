use crate::configuration::{KeywordFormatter, KeywordPreprocessor};
use crate::node::{RefinedArgumentsAtom, RefinedArgumentsNode};
use crate::python_side::builtin_schemas;
use crate::two_words_keyword_isolator::TwoWordKeywordMatcher;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyTuple};
use pyo3::{FromPyObject, PyAny};
use std::cmp::min;
use std::collections::HashMap;
use std::sync::LazyLock;

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
pub enum SecondKeyword {
    String(String),
    Any,
}

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
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

#[derive(Clone, Debug, FromPyObject)]
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
            } else {
                let value = argument.get_keyword_value();
                let value = value.as_ref();
                if is_one_of_keywords(value, &schema.options) {
                    self.flush_accumulators();
                    self.groups.push(RefinedArgumentsAtom::OptionArgument {
                        keyword: Box::new(argument),
                    });
                } else if is_one_of_keywords(value, &schema.one_value_keywords) {
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
                } else if argument.is_phantom()
                    || is_one_of_keywords(value, &schema.multi_value_keywords)
                {
                    self.flush_accumulators();
                    self.accumulator.kind = AccumulatorKind::Nodes;
                    self.accumulator.nodes = vec![argument];
                } else if !self.accumulator.nodes.is_empty() {
                    self.accumulator.nodes.append(&mut self.comment_accumulator);
                    self.accumulator.nodes.push(argument);
                } else {
                    if !matches!(self.accumulator.kind, AccumulatorKind::PositionalArguments) {
                        self.accumulator.kind = AccumulatorKind::PositionalArguments;
                    }
                    self.accumulator.nodes.append(&mut self.comment_accumulator);
                    self.accumulator.nodes.push(argument);
                }
            }
        }

        self.flush_accumulators();
    }
}

impl ArgumentSchema {
    fn is_one_of_keywords(&self, node: &RefinedArgumentsAtom) -> bool {
        if node.is_phantom() {
            return true;
        }
        let value = node.get_keyword_value();
        let value = value.as_ref();
        is_one_of_keywords(value, &self.options)
            || is_one_of_keywords(value, &self.one_value_keywords)
            || is_one_of_keywords(value, &self.multi_value_keywords)
    }

    fn find_pivot(&self, arguments: &[RefinedArgumentsAtom]) -> Option<usize> {
        for (index, argument) in arguments.iter().enumerate() {
            if self.is_one_of_keywords(argument) {
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
        let value = argument.get_keyword_value();
        let value = value.as_ref();
        for (item, schema) in &self.sections {
            if is_one_of_keywords(value, std::slice::from_ref(item)) {
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
            if section_schema.is_some_and(|x| x.is_one_of_keywords(&argument)) {
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

pub struct KeywordValue {
    first: String,
    second: Option<String>,
}

pub fn is_one_of_keywords(
    keyword_value: Option<&KeywordValue>,
    matchers: &[KeywordMatcher],
) -> bool {
    let Some(keyword_value) = keyword_value else {
        return false;
    };

    match keyword_value {
        KeywordValue {
            first,
            second: None,
        } => {
            for matcher in matchers {
                if (matcher.first.as_str() == first) && matcher.second.is_none() {
                    return true;
                }
            }
            false
        }
        KeywordValue {
            first,
            second: Some(second),
        } => {
            for matcher in matchers {
                if matcher.first.as_str() != first {
                    continue;
                }

                match &matcher.second {
                    None | Some(SecondKeyword::Any) => {
                        return true;
                    }
                    Some(SecondKeyword::String(matcher_second)) => {
                        if matcher_second.as_str() == second {
                            return true;
                        }
                    }
                }
            }
            false
        }
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

    pub fn get_keyword_value(&self) -> Option<KeywordValue> {
        match self {
            Self::Atom(atom) => atom.get_value().map(|value| KeywordValue {
                first: value,
                second: None,
            }),
            Self::KeywordArgument { first, second, .. } => Some(KeywordValue {
                first: first.get_value()?,
                second: second.get_value(),
            }),
            Self::OptionArgument { keyword }
            | Self::OneValueArgument { keyword, .. }
            | Self::MultiValueArgument { keyword, .. }
            | Self::Section {
                header: keyword, ..
            }
            | Self::Pair { first: keyword, .. } => keyword.get_keyword_value(),
            Self::BinaryOperation { .. }
            | Self::UnaryOperation { .. }
            | Self::PositionalArguments(_) => None,
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
                if is_one_of_keywords(one_behind_node.get_keyword_value().as_ref(), operators) {
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
                if is_one_of_keywords(one_behind_node.get_keyword_value().as_ref(), operators) {
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
    static UNARY_OPERATORS: LazyLock<[KeywordMatcher; 12]> = LazyLock::new(|| {
        [
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
        .map(single_word_matcher)
    });
    static BINARY_OPERATORS: LazyLock<[KeywordMatcher; 19]> = LazyLock::new(|| {
        [
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
        .map(single_word_matcher)
    });
    static NOT_OPERATOR: LazyLock<[KeywordMatcher; 1]> =
        LazyLock::new(|| [single_word_matcher("NOT")]);
    static AND_OPERATOR: LazyLock<[KeywordMatcher; 1]> =
        LazyLock::new(|| [single_word_matcher("AND")]);
    static OR_OPERATOR: LazyLock<[KeywordMatcher; 1]> =
        LazyLock::new(|| [single_word_matcher("OR")]);

    isolate_unary_operators(
        OR_OPERATOR.as_ref(),
        isolate_unary_operators(
            AND_OPERATOR.as_ref(),
            isolate_unary_operators(
                NOT_OPERATOR.as_ref(),
                isolate_binary_tests(
                    BINARY_OPERATORS.as_ref(),
                    isolate_unary_operators(UNARY_OPERATORS.as_ref(), arguments),
                ),
            ),
        ),
    )
}

pub type Signatures = HashMap<Option<KeywordMatcher>, ArgumentSchema>;

#[allow(clippy::large_enum_variant)]
#[derive(Clone, Debug, FromPyObject)]
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

#[derive(Clone, Debug, FromPyObject)]
pub struct CommandSchema {
    pub block_end: Option<String>,
    pub canonical_name: Option<String>,
    pub inhibit_favour_expansion: bool,
    pub details: CommandSchemaDetails,
}

pub type CommandSchemaMapping = HashMap<String, CommandSchema>;

pub struct CommandSchemas {
    pub definition_schemas: CommandSchemaMapping,
    pub extension_schemas: CommandSchemaMapping,
}

impl CommandSchemas {
    pub fn get(&self, key: &str) -> Option<&CommandSchema> {
        self.definition_schemas.get(key).or_else(|| {
            self.extension_schemas
                .get(key)
                .or_else(|| builtin_schemas().get(key))
        })
    }

    pub fn contains_key(&self, key: &str) -> bool {
        self.definition_schemas.contains_key(key)
            || self.extension_schemas.contains_key(key)
            || builtin_schemas().contains_key(key)
    }
}
