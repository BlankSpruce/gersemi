use crate::argument_schema::{is_keyword, SecondKeyword};
use crate::node::{Node, Nodes};
use crate::parser::tree;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyTuple};
use pyo3::{FromPyObject, PyAny};

pub struct TwoWordKeywordMatcher {
    first: String,
    second: SecondKeyword,
}

impl FromPyObject<'_, '_> for TwoWordKeywordMatcher {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        let (first, second) = if obj.is_instance_of::<PyTuple>() {
            let (left, right) = (obj.get_item(0)?, obj.get_item(1)?);

            let left = left.cast::<PyString>()?.str()?.to_string();
            let right = if right.is_instance_of::<PyString>() {
                SecondKeyword::String(right.cast::<PyString>()?.str()?.to_string())
            } else {
                SecondKeyword::Any
            };

            (left, right)
        } else {
            return Err(PyRuntimeError::new_err("Invalid keyword matcher"));
        };

        Ok(TwoWordKeywordMatcher { first, second })
    }
}

fn isolate_two_words_keyword(matcher: &TwoWordKeywordMatcher, arguments: Nodes) -> Nodes {
    let mut result = Nodes::new();
    let mut accumulator = Nodes::new();
    for argument in arguments {
        if accumulator.is_empty() {
            match &argument {
                Node::Token { .. } => {
                    result.push(argument);
                }
                Node::Tree { data, children } => {
                    if is_keyword(&matcher.first, data, children) {
                        accumulator = vec![argument];
                    } else {
                        result.push(argument);
                    }
                }
            }
        } else if argument.is_comment() {
            accumulator.push(argument);
        } else {
            let is_keyword_argument = match &matcher.second {
                SecondKeyword::Any => true,
                SecondKeyword::String(m) => match &argument {
                    Node::Token { .. } => false,
                    Node::Tree { data, children } => is_keyword(m, data, children),
                },
            };
            if is_keyword_argument {
                accumulator.push(argument);
                result.push(tree("keyword_argument", std::mem::take(&mut accumulator)));
            } else {
                result.append(&mut accumulator);
                accumulator = vec![argument];
            }
        }
    }

    result.append(&mut accumulator);
    result
}

pub fn preprocess_arguments(
    two_words_keywords: Vec<TwoWordKeywordMatcher>,
    mut arguments: Nodes,
) -> Nodes {
    for matcher in two_words_keywords {
        arguments = isolate_two_words_keyword(&matcher, arguments);
    }
    arguments
}
