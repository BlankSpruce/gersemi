use crate::argument_schema::is_keyword;
use crate::node::{Command, CommandInvocation, FileElement, Node, Nodes, Start};
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

struct CustomCommandInterpreter<'a> {
    parser: &'a Parser,
    stack: HashMap<String, Vec<String>>,
    found_commands: HashMap<String, Vec<CustomCommand>>,
    filepath: String,
}

fn find_token<'a>(node: &'a Node, token_type: &str) -> Option<&'a String> {
    match node {
        Node::Token { type_, value, .. } => {
            if type_.as_str() == token_type {
                Some(value)
            } else {
                None
            }
        }
        Node::Tree { children, .. } => {
            for child in children {
                if let Some(result) = find_token(child, token_type) {
                    return Some(result);
                }
            }
            None
        }
    }
}

fn should_definition_be_ignored(children: &Nodes) -> bool {
    let Some(Node::Tree { children, .. }) = children.get(1) else {
        return false;
    };

    for child in children {
        if find_token(child, "HELPER_IGNORE_THIS_DEFINITION").is_some() {
            return true;
        }
    }
    false
}

fn get_block_end(children: &Nodes) -> Option<String> {
    let Some(Node::Tree { children, .. }) = children.get(1) else {
        return None;
    };

    for child in children {
        if let Some(value) = find_token(child, "HELPER_BLOCK_END_COMMAND") {
            return Some(value.clone());
        }
    }
    None
}

fn bracket_argument(nodes: &Nodes) -> String {
    nodes
        .iter()
        .map(|child| match child {
            Node::Token { value, .. } => value.clone(),
            Node::Tree { .. } => String::new(),
        })
        .collect::<String>()
}

fn complex_argument(nodes: &Nodes) -> String {
    match nodes.first() {
        None => String::new(),
        Some(Node::Token { value, .. }) => value.clone(),
        Some(Node::Tree { children, .. }) => children
            .iter()
            .map(|child| match child {
                Node::Token { value, .. } => value.clone(),
                Node::Tree { .. } => String::new(),
            })
            .collect::<String>(),
    }
}

fn argument(node: &Node) -> String {
    match node {
        Node::Tree { data, children } => match data.as_str() {
            "unquoted_argument" => match children.first() {
                None => String::new(),
                Some(Node::Tree { children, .. }) => match children.first() {
                    None => String::new(),
                    Some(node) => argument(node),
                },
                Some(Node::Token { value, .. }) => value.clone(),
            },
            "quoted_argument" => match children.first() {
                None => String::new(),
                Some(Node::Tree { children, .. }) => match children.first() {
                    None => String::new(),
                    Some(node) => argument(node),
                },
                Some(Node::Token { value, .. }) => {
                    let mut value = value.chars();
                    value.next();
                    value.next_back();
                    value.as_str().to_string()
                }
            },
            "bracket_argument" => bracket_argument(children),
            "complex_argument" => complex_argument(children),
            "commented_argument" => argument(children.first().unwrap()),
            _ => String::new(),
        },
        Node::Token { value, .. } => value.clone(),
    }
}

fn new_command(children: &Nodes) -> Option<(&Node, Vec<String>)> {
    let (
        Some(Node::Token {
            value: identifier, ..
        }),
        Some(Node::Tree {
            children: arguments,
            ..
        }),
    ) = (children.first(), children.get(1))
    else {
        return None;
    };

    let is_function_or_macro =
        (identifier.as_str() == "function") || (identifier.as_str() == "macro");
    if !is_function_or_macro {
        return None;
    }

    let positional_arguments = &arguments[1..];
    let name = arguments.first().unwrap();

    let positional_arguments = positional_arguments.iter().map(argument).collect();
    Some((name, positional_arguments))
}

fn block_begin(node: &Node) -> Option<(&Node, Vec<String>)> {
    match node {
        Node::Token { .. } => None,
        Node::Tree { data, children } => match data.as_str() {
            "command_element" => {
                let Some(Node::Tree { children, .. }) = children.first() else {
                    return None;
                };

                new_command(children)
            }
            _ => new_command(children),
        },
    }
}

fn get_hints(children: &Nodes) -> Vec<String> {
    let Some(Node::Tree { children, .. }) = children.get(1) else {
        return vec![];
    };

    let mut result = Vec::<String>::new();
    for child in children {
        if let Some(value) = find_token(child, "HELPER_USE_HINT") {
            result.push(value.clone());
        }
    }
    result
}

fn get_command_start(node: &Node) -> (Option<usize>, Option<usize>) {
    match node {
        Node::Tree { children, .. } => get_command_start(children.first().unwrap()),
        Node::Token { line, column, .. } => (*line, *column),
    }
}

const BLOCK_END: &str = "gersemi: block_end ";
const HINTS: &str = "gersemi: hints";
const IGNORE: &str = "gersemi: ignore";

fn helper_token(type_: &str, value: &str) -> Node {
    Node::Token {
        type_: type_.to_string(),
        value: value.to_string(),
        line: None,
        column: None,
    }
}

fn simplify(node: Node) -> Option<Node> {
    match node {
        Node::Token { .. } => Some(node),
        Node::Tree { data, children } => {
            let children: Nodes = children.into_iter().filter_map(simplify).collect();
            match data.as_str() {
                "bracket_comment" => None,
                "line_comment" => {
                    let Some(Node::Token { value, .. }) = children.get(1) else {
                        return None;
                    };
                    let value = value.trim();
                    if let Some((_, content)) = value.split_once(BLOCK_END) {
                        Some(helper_token("HELPER_BLOCK_END_COMMAND", content))
                    } else if let Some((_, content)) = value.split_once(HINTS) {
                        Some(helper_token("HELPER_USE_HINT", content))
                    } else if value.starts_with(IGNORE) {
                        Some(helper_token("HELPER_IGNORE_THIS_DEFINITION", ""))
                    } else {
                        None
                    }
                }
                "non_command_element" => {
                    if children.len() != 1 {
                        return None;
                    }

                    let Some(Node::Token {
                        type_,
                        value,
                        line,
                        column,
                    }) = children.first()
                    else {
                        return None;
                    };

                    if type_.starts_with("HELPER_") {
                        Some(Node::Token {
                            type_: type_.clone(),
                            value: value.clone(),
                            line: *line,
                            column: *column,
                        })
                    } else {
                        None
                    }
                }
                _ => Some(Node::Tree { data, children }),
            }
        }
    }
}

fn simplify_invocation(node: CommandInvocation) -> CommandInvocation {
    match node {
        CommandInvocation::KnownCommand {
            identifier,
            arguments,
        } => CommandInvocation::KnownCommand {
            identifier,
            arguments: simplify(arguments).unwrap(),
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
        FileElement::Node(node) => simplify(node).map(FileElement::Node),
        FileElement::StandaloneIdentifier { .. } => None,
        FileElement::NonCommandElement { line_comment, .. } => match line_comment {
            None => None,
            Some(node) => match simplify(node) {
                None => None,
                Some(node) => match node {
                    Node::Tree { .. } => None,
                    Node::Token { ref type_, .. } => {
                        if type_.starts_with("HELPER_") {
                            Some(FileElement::Node(node))
                        } else {
                            None
                        }
                    }
                },
            },
        },
        FileElement::NewlineOrGap { .. } => None,
    }
}

impl CustomCommandInterpreter<'_> {
    fn get_subinterpreter(&self) -> Self {
        Self {
            parser: self.parser,
            stack: self.stack.clone(),
            found_commands: HashMap::new(),
            filepath: self.filepath.clone(),
        }
    }

    fn block_body(&mut self, node: &Node) -> Option<Keywords> {
        let Node::Tree { children, .. } = node else {
            return None;
        };

        let mut result: Option<Keywords> = None;
        for child in children {
            let Node::Tree { data, children } = child else {
                continue;
            };

            let item = match data.as_str() {
                "command_element" => {
                    let Some(Node::Tree { data, children }) = children.first() else {
                        continue;
                    };
                    if data.as_str() == "command_invocation" {
                        self.command_invocation(children)
                    } else {
                        None
                    }
                }
                "command_invocation" => self.command_invocation(children),
                "block" => {
                    self.block(children);
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
        name: &Node,
        positional_arguments: Vec<String>,
        keywords: Keywords,
        block_end: Option<String>,
    ) {
        let (line, column) = get_command_start(name);
        let name = argument(name);

        let key = name.to_lowercase();
        if !self.found_commands.contains_key(&key) {
            self.found_commands.insert(key.clone(), vec![]);
        }

        let entry = (
            CustomCommandContent {
                canonical_name: name.clone(),
                positional_arguments,
                keywords,
                block_end,
            },
            format!(
                "{}:{}:{}",
                self.filepath,
                line.unwrap_or(0),
                column.unwrap_or(0)
            ),
        );
        self.found_commands.get_mut(&key).unwrap().push(entry);
    }

    fn block(&mut self, children: &Nodes) {
        if children.len() < 3 {
            return;
        }

        if should_definition_be_ignored(children) {
            return;
        }

        let block_end = get_block_end(children);
        let mut subinterpreter = self.get_subinterpreter();
        let command_node = block_begin(children.first().unwrap());
        let body = subinterpreter.block_body(children.get(1).unwrap());

        self.found_commands.extend(subinterpreter.found_commands);
        let Some((name, positional_arguments)) = command_node else {
            return;
        };

        let keywords = match body {
            None => Keywords {
                options: Vec::new(),
                one_value_keywords: Vec::new(),
                multi_value_keywords: Vec::new(),
                hints: Vec::new(),
            },
            Some(body) => {
                let mut result = body;
                result.hints = get_hints(children);
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

    fn cmake_parse_arguments(&self, children: &Nodes) -> Option<Keywords> {
        let Some(Node::Tree {
            data,
            children: first_children,
        }) = children.first()
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
            options: self.eval_variables(argument(options)),
            one_value_keywords: self.eval_variables(argument(one_value_arguments)),
            multi_value_keywords: self.eval_variables(argument(multi_value_arguments)),
            hints: vec![],
        })
    }

    fn set(&mut self, arguments: &Nodes) {
        let arguments = arguments.iter().map(argument).collect::<Vec<String>>();
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

    fn command_invocation(&mut self, children: &Nodes) -> Option<Keywords> {
        let (
            Some(Node::Token {
                value: identifier, ..
            }),
            Some(Node::Tree {
                children: arguments,
                ..
            }),
        ) = (children.first(), children.get(1))
        else {
            return None;
        };

        match identifier.as_str() {
            "cmake_parse_arguments" => self.cmake_parse_arguments(arguments),
            "set" => {
                self.set(arguments);
                None
            }
            _ => None,
        }
    }

    fn start(&mut self, node: Start) {
        for child in node.children.into_iter().filter_map(simplify_file_element) {
            match child {
                FileElement::Block { start, body, end } => {
                    let children = vec![
                        start.into_node(),
                        Node::Tree {
                            data: "block_body".to_string(),
                            children: body.into_iter().map(FileElement::into_node).collect(),
                        },
                        end.into_node(),
                    ];
                    self.block(&children);
                }
                FileElement::Command(command) => match command {
                    Command::Element {
                        command_invocation: node,
                        ..
                    }
                    | Command::Invocation(node) => match node {
                        CommandInvocation::KnownCommand {
                            identifier,
                            arguments,
                        } => {
                            let children = vec![identifier, arguments];
                            self.command_invocation(&children);
                        }
                        CommandInvocation::CustomCommand { .. } => (),
                    },
                },
                FileElement::Node(_) => (),
                FileElement::NonCommandElement { .. } => (),
                FileElement::StandaloneIdentifier { .. } => (),
                FileElement::NewlineOrGap { .. } => (),
            }
        }
    }
}

pub fn find_custom_command_definitions(
    parser: &Parser,
    filepath: String,
) -> HashMap<String, Vec<CustomCommand>> {
    let mut interpreter = CustomCommandInterpreter {
        parser,
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
