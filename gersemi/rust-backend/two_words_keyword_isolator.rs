use crate::argument_schema::KeywordMatcher;
use crate::node::{ArgumentsNode, RefinedArgumentsAtom, RefinedArgumentsNode};

fn isolate_two_words_keyword<'a>(
    matcher: &KeywordMatcher,
    arguments: RefinedArgumentsNode<'a>,
) -> RefinedArgumentsNode<'a> {
    let mut result = RefinedArgumentsNode::with_capacity(arguments.len());
    let mut accumulator = ArgumentsNode::with_capacity(2);
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
                None => true,
                Some(m) => match argument.get_value() {
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

pub fn preprocess_arguments<'a>(
    two_words_keywords: &Vec<KeywordMatcher>,
    mut arguments: RefinedArgumentsNode<'a>,
) -> RefinedArgumentsNode<'a> {
    for matcher in two_words_keywords {
        arguments = isolate_two_words_keyword(matcher, arguments);
    }
    arguments
}
