use crate::argument_schema::is_keyword;
use crate::node::{
    Argument, Arguments, ArgumentsAtom, ArgumentsNode, Command, CommandInvocation, FileElement,
    HelperNode, LineComment, Node, Position, Start,
};
use crate::parser::Parser;
use pyo3::IntoPyObject;
use std::collections::HashMap;

#[derive(IntoPyObject)]
pub struct Keywords {
    options: Vec<String>,
    one_value_keywords: Vec<String>,
    multi_value_keywords: Vec<String>,
    hints: Vec<String>,
}

#[derive(IntoPyObject)]
pub struct CustomCommandContent {
    canonical_name: String,
    positional_arguments: Vec<String>,
    keywords: Keywords,
    block_end: Option<String>,
}

pub type CustomCommand = (CustomCommandContent, String);

struct CustomCommandInterpreter {
    stack: HashMap<String, Vec<String>>,
    found_commands: HashMap<String, Vec<CustomCommand>>,
    filepath: String,
}

fn should_definition_be_ignored(body: &Vec<FileElement>) -> bool {
    for child in body {
        if let FileElement::HelperNode(HelperNode::IgnoreThisDefinition) = child {
            return true;
        }
    }
    false
}

fn get_block_end(body: &Vec<FileElement>) -> Option<String> {
    for child in body {
        if let FileElement::HelperNode(HelperNode::BlockEndCommand { value }) = child {
            return Some(value.clone());
        }
    }
    None
}

fn argument(node: Argument) -> String {
    match node {
        Argument::Complex { arguments } => arguments
            .into_iter()
            .filter_map(|x| match x {
                ArgumentsAtom::Argument(node)
                | ArgumentsAtom::CommentedArgument { argument: node, .. } => Some(argument(node)),
                ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
            })
            .collect::<Vec<_>>()
            .join(" "),
        Argument::Bracket { value, .. }
        | Argument::Quoted { value, .. }
        | Argument::Unquoted { value, .. } => value,
    }
}

fn into_arguments(node: ArgumentsNode) -> Arguments {
    node.into_iter()
        .filter_map(|x| match x {
            ArgumentsAtom::Argument(argument)
            | ArgumentsAtom::CommentedArgument { argument, .. } => Some(argument),
            ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
        })
        .collect()
}

fn new_command(identifier: &str, node: ArgumentsNode) -> Option<(Argument, Vec<String>)> {
    let is_function_or_macro = (identifier == "function") || (identifier == "macro");
    if !is_function_or_macro {
        return None;
    }

    let mut arguments: Arguments = into_arguments(node);
    let positional_arguments: Arguments = arguments.drain(1..).collect();
    let name = arguments.pop();

    let positional_arguments = positional_arguments.into_iter().map(argument).collect();
    Some((name?, positional_arguments))
}

fn block_begin(node: Command) -> Option<(Argument, Vec<String>)> {
    match node {
        Command::Element {
            command_invocation: node,
            ..
        }
        | Command::Invocation(node) => {
            let CommandInvocation::KnownCommand {
                identifier,
                arguments,
            } = node
            else {
                return None;
            };
            new_command(&identifier, arguments)
        }
    }
}

fn get_hints(body: &Vec<FileElement>) -> Vec<String> {
    let mut result = Vec::<String>::new();
    for child in body {
        if let FileElement::HelperNode(HelperNode::UseHint { value }) = child {
            result.push(value.clone());
        }
    }
    result
}

fn get_command_start(node: &Argument) -> Option<Position> {
    match node {
        Argument::Bracket { position, .. }
        | Argument::Quoted { position, .. }
        | Argument::Unquoted { position, .. } => position.clone(),
        Argument::Complex { arguments } => match arguments.first() {
            None => None,
            Some(node) => match node {
                ArgumentsAtom::Argument(argument)
                | ArgumentsAtom::CommentedArgument { argument, .. } => get_command_start(argument),
                ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
            },
        },
    }
}

const BLOCK_END: &str = "gersemi: block_end ";
const HINTS: &str = "gersemi: hints";
const IGNORE: &str = "gersemi: ignore";

fn simplify(node: ArgumentsAtom) -> Option<ArgumentsAtom> {
    match node {
        ArgumentsAtom::Argument(_) | ArgumentsAtom::CommentedArgument { .. } => Some(node),
        ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => None,
    }
}

fn simplify_invocation(node: CommandInvocation) -> CommandInvocation {
    match node {
        CommandInvocation::KnownCommand {
            identifier,
            arguments,
        } => CommandInvocation::KnownCommand {
            identifier,
            arguments: arguments.into_iter().filter_map(simplify).collect(),
        },
        CommandInvocation::CustomCommand { .. } => node,
    }
}

fn simplify_file_element(node: FileElement) -> Option<FileElement> {
    match node {
        FileElement::Block { start, body, end } => Some(FileElement::Block {
            start,
            body: body.into_iter().filter_map(simplify_file_element).collect(),
            end,
        }),
        FileElement::Command(node) => Some(FileElement::Command(match node {
            Command::Element {
                command_invocation,
                line_comment,
            } => Command::Element {
                command_invocation: simplify_invocation(command_invocation),
                line_comment,
            },
            Command::Invocation(node) => Command::Invocation(simplify_invocation(node)),
        })),
        FileElement::HelperNode(_) => Some(node),
        FileElement::NonCommandElement { line_comment, .. } => match line_comment {
            None => None,
            Some(LineComment { value }) => {
                let value = value.trim();
                if let Some((_, content)) = value.split_once(BLOCK_END) {
                    Some(FileElement::HelperNode(HelperNode::BlockEndCommand {
                        value: content.to_string(),
                    }))
                } else if let Some((_, content)) = value.split_once(HINTS) {
                    Some(FileElement::HelperNode(HelperNode::UseHint {
                        value: content.to_string(),
                    }))
                } else if value.starts_with(IGNORE) {
                    Some(FileElement::HelperNode(HelperNode::IgnoreThisDefinition))
                } else {
                    None
                }
            }
        },
        FileElement::StandaloneIdentifier { .. } | FileElement::NewlineOrGap { .. } => None,
    }
}

impl CustomCommandInterpreter {
    fn get_subinterpreter(&self) -> Self {
        Self {
            stack: self.stack.clone(),
            found_commands: HashMap::new(),
            filepath: self.filepath.clone(),
        }
    }

    fn block_body(&mut self, body: Vec<FileElement>) -> Option<Keywords> {
        let mut result: Option<Keywords> = None;
        for child in body {
            let item = match child {
                FileElement::Command(node) => self.command(node),
                FileElement::Block { start, body, .. } => {
                    self.block(start, body);
                    None
                }
                _ => None,
            };

            if item.is_some() {
                result = item;
            }
        }

        result
    }

    fn add_command(
        &mut self,
        name: Argument,
        positional_arguments: Vec<String>,
        keywords: Keywords,
        block_end: Option<String>,
    ) {
        let (line, column) = match get_command_start(&name) {
            None => (0, 0),
            Some(Position { line, column }) => (line, column),
        };
        let canonical_name = argument(name);
        self.found_commands
            .entry(canonical_name.to_lowercase())
            .or_insert(vec![])
            .push((
                CustomCommandContent {
                    canonical_name,
                    positional_arguments,
                    keywords,
                    block_end,
                },
                format!("{}:{}:{}", self.filepath, line, column),
            ));
    }

    fn block(&mut self, start: Command, body: Vec<FileElement>) {
        if should_definition_be_ignored(&body) {
            return;
        }

        let block_end = get_block_end(&body);
        let mut subinterpreter = self.get_subinterpreter();
        let command_node = block_begin(start);
        let hints = get_hints(&body);
        let keywords = subinterpreter.block_body(body);

        self.found_commands.extend(subinterpreter.found_commands);
        let Some((name, positional_arguments)) = command_node else {
            return;
        };

        let keywords = match keywords {
            None => Keywords {
                options: Vec::new(),
                one_value_keywords: Vec::new(),
                multi_value_keywords: Vec::new(),
                hints: Vec::new(),
            },
            Some(keywords) => {
                let mut result = keywords;
                result.hints = hints;
                result
            }
        };

        self.add_command(name, positional_arguments, keywords, block_end);
    }

    fn eval_variables(&self, mut arg: String) -> Vec<String> {
        for (name, value) in &self.stack {
            let from_pattern = format!("${}{name}{}", "{", "}");
            let to_value = value.join(";");
            arg = arg.replace(from_pattern.as_str(), to_value.as_str());
        }
        let result = arg
            .split(';')
            .map(std::string::ToString::to_string)
            .collect();
        result
    }

    fn cmake_parse_arguments(&self, children: &Arguments) -> Option<Keywords> {
        let first_child = children.first()?.clone().into_node();
        let Node::Tree {
            ref data,
            children: ref first_children,
        } = first_child
        else {
            return None;
        };

        let parse_argv = "PARSE_ARGV".to_string();
        let part = if is_keyword(&parse_argv, data, first_children) {
            [children.get(3), children.get(4), children.get(5)]
        } else {
            [children.get(1), children.get(2), children.get(3)]
        };

        let [Some(options), Some(one_value_arguments), Some(multi_value_arguments)] = part else {
            return None;
        };

        Some(Keywords {
            options: self.eval_variables(argument(options.clone())),
            one_value_keywords: self.eval_variables(argument(one_value_arguments.clone())),
            multi_value_keywords: self.eval_variables(argument(multi_value_arguments.clone())),
            hints: vec![],
        })
    }

    fn set(&mut self, arguments: Arguments) {
        let arguments = arguments.into_iter().map(argument).collect::<Vec<String>>();
        let Some(name) = arguments.first() else {
            return;
        };
        let arguments = &arguments[1..];

        let mut result = Vec::<String>::new();
        for value in arguments.iter().map(|a| self.eval_variables(a.clone())) {
            for item in value {
                result.push(item);
            }
        }
        self.stack.insert(name.clone(), result);
    }

    fn command_invocation(&mut self, identifier: &str, arguments: Arguments) -> Option<Keywords> {
        match identifier {
            "cmake_parse_arguments" => self.cmake_parse_arguments(&arguments),
            "set" => {
                self.set(arguments);
                None
            }
            _ => None,
        }
    }

    fn command(&mut self, node: Command) -> Option<Keywords> {
        match node {
            Command::Element {
                command_invocation: node,
                ..
            }
            | Command::Invocation(node) => match node {
                CommandInvocation::KnownCommand {
                    ref identifier,
                    arguments,
                } => self.command_invocation(identifier, into_arguments(arguments)),
                CommandInvocation::CustomCommand { .. } => None,
            },
        }
    }

    fn start(&mut self, node: Start) {
        for child in node.children.into_iter().filter_map(simplify_file_element) {
            match child {
                FileElement::Block { start, body, .. } => {
                    self.block(start, body);
                }
                FileElement::Command(node) => {
                    self.command(node);
                }
                FileElement::HelperNode(_)
                | FileElement::NonCommandElement { .. }
                | FileElement::StandaloneIdentifier { .. }
                | FileElement::NewlineOrGap { .. } => (),
            }
        }
    }
}

pub fn find_custom_command_definitions(
    parser: &Parser,
    filepath: String,
) -> HashMap<String, Vec<CustomCommand>> {
    let mut interpreter = CustomCommandInterpreter {
        stack: HashMap::new(),
        found_commands: HashMap::new(),
        filepath,
    };
    let Ok(node) = parser.start() else {
        return HashMap::new();
    };
    interpreter.start(node);
    interpreter.found_commands
}
