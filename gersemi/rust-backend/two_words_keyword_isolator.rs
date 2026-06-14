use crate::argument_schema::SecondKeyword;
use crate::node::{ArgumentsNode, RefinedArgumentsAtom, RefinedArgumentsNode};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyTuple};
use pyo3::{FromPyObject, PyAny};

#[derive(Clone)]
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

fn isolate_two_words_keyword(
    matcher: &TwoWordKeywordMatcher,
    arguments: RefinedArgumentsNode,
) -> RefinedArgumentsNode {
    let mut result = RefinedArgumentsNode::new();
    let mut accumulator = ArgumentsNode::new();
    for argument in arguments {
        let RefinedArgumentsAtom::Atom(argument) = argument else {
            result.push(argument);
            continue;
        };
        if accumulator.is_empty() {
            match argument.get_value() {
                Some(value) if value == matcher.first => {
                    accumulator = vec![argument];
                }
                _ => {
                    result.push(RefinedArgumentsAtom::Atom(argument));
                }
            }
        } else if argument.is_comment() {
            accumulator.push(argument);
        } else {
            let is_keyword_argument = match &matcher.second {
                SecondKeyword::Any => true,
                SecondKeyword::String(m) => match argument.get_value() {
                    Some(value) => value == *m,
                    None => false,
                },
            };
            if is_keyword_argument {
                let in_between = accumulator.split_off(1);
                result.push(RefinedArgumentsAtom::KeywordArgument {
                    first: accumulator.pop().unwrap(),
                    in_between,
                    second: argument,
                });
            } else {
                result.extend(
                    std::mem::take(&mut accumulator)
                        .into_iter()
                        .map(RefinedArgumentsAtom::Atom),
                );
                accumulator = vec![argument];
            }
        }
    }

    let accumulator = std::mem::take(&mut accumulator);
    result.extend(accumulator.into_iter().map(RefinedArgumentsAtom::Atom));
    result
}

pub fn preprocess_arguments(
    two_words_keywords: &Vec<TwoWordKeywordMatcher>,
    mut arguments: RefinedArgumentsNode,
) -> RefinedArgumentsNode {
    for matcher in two_words_keywords {
        arguments = isolate_two_words_keyword(matcher, arguments);
    }
    arguments
}
