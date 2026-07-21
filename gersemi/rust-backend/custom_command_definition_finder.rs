use crate::argument_schema::CommandSchemas;
use crate::configuration::Configuration;
use crate::gersemi_rust_backend::warn;
use crate::node::{
    Argument, Arguments, ArgumentsAtom, ArgumentsNode, BracketArgument, Command, CommandInvocation,
    FileElement, Position, Start,
};
use crate::parser::Parser;
use crate::utils::{get_files, normalize_newlines, read_code};
use pyo3::{PyResult, Python};
use rayon::iter::{IntoParallelIterator, ParallelIterator};
use std::collections::HashMap;
use std::fmt::Write;

pub struct Keywords {
    pub options: Vec<String>,
    pub one_value_keywords: Vec<String>,
    pub multi_value_keywords: Vec<String>,
    pub hints: Vec<String>,
}

pub struct CustomCommandContent {
    pub canonical_name: String,
    pub positional_arguments: Vec<String>,
    pub keywords: Keywords,
    pub block_end: Option<String>,
}

pub type CustomCommand = (CustomCommandContent, String);

struct CustomCommandInterpreter {
    stack: HashMap<String, Vec<String>>,
    found_commands: HashMap<String, Vec<CustomCommand>>,
    filepath: String,
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

    let positional_arguments = positional_arguments
        .iter()
        .map(Argument::get_value)
        .collect();
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

fn get_command_start(node: &Argument) -> Option<Position> {
    match node {
        Argument::Bracket(BracketArgument { position, .. })
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
        Argument::InlineHint { .. } => None,
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
        name: &Argument,
        positional_arguments: Vec<String>,
        keywords: Keywords,
        block_end: Option<String>,
    ) {
        let (line, column) = match get_command_start(name) {
            None => (0, 0),
            Some(Position { line, column }) => (line, column),
        };
        let canonical_name = name.get_value();
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
        if body.iter().any(FileElement::is_ignore_directive) {
            return;
        }

        let block_end = body.iter().find_map(FileElement::get_block_end);
        let mut subinterpreter = self.get_subinterpreter();
        let command_node = block_begin(start);
        let hints = body.iter().filter_map(FileElement::get_hint).collect();
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

        self.add_command(&name, positional_arguments, keywords, block_end);
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
        let first_child = children.first()?.get_value();
        let part = match first_child.as_str() {
            "PARSE_ARGV" => [children.get(3), children.get(4), children.get(5)],
            "PARSE_ARGN" => [children.get(2), children.get(3), children.get(4)],
            _ => [children.get(1), children.get(2), children.get(3)],
        };

        let [Some(options), Some(one_value_arguments), Some(multi_value_arguments)] = part else {
            return None;
        };

        Some(Keywords {
            options: self.eval_variables(options.get_value()),
            one_value_keywords: self.eval_variables(one_value_arguments.get_value()),
            multi_value_keywords: self.eval_variables(multi_value_arguments.get_value()),
            hints: vec![],
        })
    }

    fn set(&mut self, arguments: &Arguments) {
        let arguments = arguments
            .iter()
            .map(Argument::get_value)
            .collect::<Vec<String>>();
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

    fn command_invocation(&mut self, identifier: &str, arguments: &Arguments) -> Option<Keywords> {
        match identifier {
            "cmake_parse_arguments" => self.cmake_parse_arguments(arguments),
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
                } => self.command_invocation(identifier, &into_arguments(arguments)),
                CommandInvocation::CustomCommand { .. } => None,
            },
        }
    }

    fn start(&mut self, node: Start) {
        for child in node.children {
            match child {
                FileElement::Block { start, body, .. } => {
                    self.block(start, body);
                }
                FileElement::Command(node) => {
                    self.command(node);
                }
                FileElement::NonCommandElement { .. }
                | FileElement::StandaloneIdentifier { .. }
                | FileElement::NewlineOrGap { .. } => (),
            }
        }
    }
}

fn has_custom_command_definition(code: &str) -> bool {
    let code = code.to_lowercase();
    (code.contains("function") && code.contains("endfunction"))
        || (code.contains("macro") && code.contains("endmacro"))
}

pub fn find_custom_command_definitions(
    text: String,
    filepath: String,
) -> PyResult<HashMap<String, Vec<CustomCommand>>> {
    if !has_custom_command_definition(&text) {
        return Ok(HashMap::new());
    }

    let schemas = CommandSchemas {
        definition_schemas: HashMap::new(),
        extension_schemas: HashMap::new(),
    };
    let parser = Parser::new(text, &schemas);

    let mut interpreter = CustomCommandInterpreter {
        stack: HashMap::new(),
        found_commands: HashMap::new(),
        filepath,
    };
    let node = parser.start()?;
    interpreter.start(node);
    Ok(interpreter.found_commands)
}

type Definitions = Vec<(String, Vec<CustomCommand>)>;

fn check_conflicting_definitions(defs: &Definitions) {
    for (name, info) in defs {
        if info.len() <= 1 {
            continue;
        }

        let mut warning = format!("Warning: conflicting definitions for '{name}':");
        let mut locations: Vec<_> = info.iter().map(|(_, location)| location).collect();
        locations.sort();

        for (index, location) in (0..).zip(locations) {
            let kind = if index == 0 { "(used)   " } else { "(ignored)" };
            let _ = write!(warning, "\n{kind} {location}");
        }
        warn(warning);
    }
}

pub fn find_all_custom_command_definitions(
    py: Python,
    configuration: &Configuration,
) -> PyResult<Definitions> {
    let mut result = Definitions::new();

    let files = get_files(
        configuration.outcome.definitions.clone(),
        configuration.control.respect_ignore_files,
    )?;
    let all_defs = py.detach(|| {
        files
            .into_par_iter()
            .panic_fuse()
            .map(|f| {
                Python::attach(|py| py.check_signals().unwrap());

                let path = f.to_str().unwrap_or("---").to_string();
                match read_code(&f) {
                    Ok(code) => {
                        let code = normalize_newlines(&code);
                        match find_custom_command_definitions(code, path.clone()) {
                            Ok(def) => Ok(def),
                            Err(err) => Err((path, err)),
                        }
                    }
                    Err(err) => Err((path, err)),
                }
            })
            .collect::<Vec<_>>()
    });

    for defs in all_defs {
        let defs = match defs {
            Err((path, err)) => {
                warn(format!(
                    "{path}:{}",
                    Python::attach(|py| err.value(py).to_string())
                ));
                continue;
            }
            Ok(defs) => defs,
        };
        for (name, mut info) in defs {
            match result
                .iter_mut()
                .find(|(command, _)| command.as_str() == name)
            {
                None => {
                    result.push((name, info));
                }
                Some((_, values)) => {
                    values.append(&mut info);
                }
            }
        }
    }

    check_conflicting_definitions(&result);

    Ok(result)
}
