use crate::argument_schema::{CommandSchema, CommandSchemas};
use crate::node::{
    Argument, ArgumentsAtom, ArgumentsNode, BracketArgument, BracketComment, Command,
    CommandInvocation, CommentedArgumentComment, FileElement, LineComment, Position, Start,
};
use pyo3::PyErr;
use regex::Regex;
use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

struct BlockCommand {
    re: regex::Regex,
}

pub struct Parser<'a> {
    text: String,
    line_offsets: Vec<usize>,
    blocks: Vec<(String, BlockCommand)>,
    schemas: &'a CommandSchemas,
}

pub enum ErrorType {
    GenericParsingError,
    UnbalancedBlock,
    UnbalancedBrackets,
    UnbalancedParentheses,
}

pub struct Error {
    pub error_type: ErrorType,
    pub explanation: String,
    pub line: usize,
    pub column: usize,
}

const ESCAPE_SEQUENCE_R: &str = r"\\([^A-Za-z0-9]|[nrt])";
const IDENTIFIER_R: &str = r"^([A-Za-z_@][A-Za-z0-9_@]*)[ \t]*";
const MAKE_STYLE_REFERENCE_R: &str = r##"\$\([^\)\n\"#]+?\)"##;
const QUOTED_CONTINUATION_R: &str = r"\\\n";
const QUOTED_ELEMENT_R: &str = r#"[^\\\"]|\n"#;

pub fn quoted_argument_pattern() -> &'static str {
    static RE: LazyLock<String> = LazyLock::new(|| {
        format!(r#""({QUOTED_ELEMENT_R}|{ESCAPE_SEQUENCE_R}|{QUOTED_CONTINUATION_R})*?""#)
    });
    RE.as_str()
}

fn unquoted_legacy_pattern() -> String {
    format!(r#"[^\s\(\)#\"\\]+{}"#, quoted_argument_pattern())
}

fn unquoted_argument_pattern() -> &'static str {
    static RE: LazyLock<String> = LazyLock::new(|| {
        format!(
            "^(({}|{}|{}|{}|{})+)",
            unquoted_legacy_pattern(),
            MAKE_STYLE_REFERENCE_R,
            ESCAPE_SEQUENCE_R,
            r#"[^\$\s\(\)#\"\\]+"#,
            r#"[^\s\(\)#\"\\]"#
        )
    });
    RE.as_str()
}

fn bracket_argument_pattern(number_of_equal_signs: usize) -> String {
    let equal_signs = "=".repeat(number_of_equal_signs);
    format!(r"^([\s\S]+?)\]{equal_signs}\]")
}

pub fn regex(pattern: &str) -> Regex {
    static REGEXES: LazyLock<Mutex<HashMap<String, Regex>>> =
        LazyLock::new(|| Mutex::new(HashMap::<String, Regex>::new()));

    let mut regexes = REGEXES.lock().unwrap();
    regexes
        .entry(pattern.to_string())
        .or_insert_with(|| Regex::new(pattern).unwrap())
        .clone()
}

impl Parser<'_> {
    pub fn new(text: String, schemas: &CommandSchemas) -> Parser<'_> {
        let line_offsets = text
            .chars()
            .enumerate()
            .filter(|(_, c)| *c == '\n')
            .map(|(i, _)| i)
            .collect::<Vec<_>>();
        Parser {
            text,
            line_offsets,
            blocks: prepare_blocks(schemas),
            schemas,
        }
    }

    fn line(&self, offset: usize) -> usize {
        self.line_offsets
            .iter()
            .take_while(|&line_offset| *line_offset < offset)
            .count()
    }

    fn column(&self, offset: usize) -> usize {
        match self.text[..offset].rfind('\n') {
            None => offset + 1,
            Some(value) => offset - value,
        }
    }

    fn error(&self, offset: usize, error_type: ErrorType) -> Error {
        let line = self.line(offset);
        let column = if line == 0 {
            offset
        } else {
            self.column(offset)
        };
        let faulty_line = self.text.lines().nth(line).unwrap_or("");
        let explanation = format!("{}\n{}^\n", faulty_line, " ".repeat(column));
        Error {
            error_type,
            explanation,
            line: line + 1,
            column: column + 1,
        }
    }

    fn unbalanced_parentheses(&self, offset: usize) -> Error {
        self.error(offset, ErrorType::UnbalancedParentheses)
    }

    fn unbalanced_brackets(&self, offset: usize) -> Error {
        self.error(offset, ErrorType::UnbalancedBrackets)
    }

    fn unbalanced_block(&self, offset: usize) -> Error {
        self.error(offset, ErrorType::UnbalancedBlock)
    }

    fn generic_parsing_error(&self, offset: usize) -> Error {
        self.error(offset, ErrorType::GenericParsingError)
    }

    fn position(&self, offset: usize) -> Position {
        Position {
            line: self.line(offset) + 1,
            column: self.column(offset),
        }
    }

    fn bracket_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Argument, usize)>, Error> {
        static RE_START: LazyLock<Regex> = LazyLock::new(|| regex(r"^\[=*\["));
        match RE_START.find(&self.text[offset..]) {
            None => Ok(None),
            Some(matched_left_bracket) => {
                let bracket_width = matched_left_bracket.len() - 2;
                let re_pattern = bracket_argument_pattern(bracket_width);
                let re = regex(re_pattern.as_str());
                let offset = offset + bracket_width + 2;
                match re.find(&self.text[offset..]) {
                    None => Err(self.unbalanced_brackets(offset)),
                    Some(value) => Ok(Some((
                        Argument::Bracket(BracketArgument {
                            bracket_width,
                            value: value.as_str()[..value.len() - bracket_width - 2].to_string(),
                            position: {
                                if compute_position {
                                    Some(self.position(offset))
                                } else {
                                    None
                                }
                            },
                        }),
                        self.skip_space(offset + value.len()),
                    ))),
                }
            }
        }
    }

    fn raw_terminal(&self, re: &regex::Regex, offset: usize) -> Option<(String, usize)> {
        match re.captures(&self.text[offset..]) {
            None => None,
            Some(captures) => captures.get(1).map(|matched| {
                (
                    matched.as_str().to_string(),
                    offset + captures.get_match().len(),
                )
            }),
        }
    }

    fn pound_sign(&self, offset: usize) -> Option<usize> {
        if self.text[offset..].starts_with('#') {
            Some(offset + 1)
        } else {
            None
        }
    }

    fn skip_space(&self, mut offset: usize) -> usize {
        while self.text[offset..].starts_with([' ', '\t']) {
            offset += 1;
        }
        offset
    }

    fn left_paren(&self, offset: usize) -> Option<usize> {
        if self.text[offset..].starts_with('(') {
            Some(self.skip_space(offset + 1))
        } else {
            None
        }
    }

    fn right_paren(&self, offset: usize) -> Result<usize, Error> {
        if self.text[offset..].starts_with(')') {
            Ok(self.skip_space(offset + 1))
        } else {
            Err(self.unbalanced_parentheses(offset))
        }
    }

    fn newline(&self, offset: usize) -> Option<(String, usize)> {
        let mut result = offset;
        while self.text[result..].starts_with('\n') {
            result += 1;
        }

        if result == offset {
            return None;
        }

        let s = self.text[offset..result].to_string();
        Some((s, self.skip_space(result)))
    }

    fn element_t(
        &self,
        command: &BlockCommand,
        offset: usize,
    ) -> Result<Option<(Command, usize)>, Error> {
        self.command_element_t(&command.re, offset)
    }

    fn block_body(
        &self,
        end_command: &BlockCommand,
        mut offset: usize,
    ) -> Result<(Vec<FileElement>, Option<Command>, usize), Error> {
        if let Some((_, new_offset)) = self.newline_or_gap(offset) {
            offset = new_offset;
        }

        let mut result: Vec<FileElement> = vec![];
        let mut last_newline_or_gap: Option<FileElement> = None;
        loop {
            if let Some((end_command, offset)) = self.element_t(end_command, offset)? {
                return Ok((result, Some(end_command), offset));
            }

            match self.file_element(offset)? {
                Some((matched, new_offset)) => {
                    if let Some(node) = last_newline_or_gap {
                        result.push(node);
                    }
                    result.push(matched);
                    if new_offset == offset {
                        break;
                    }
                    offset = new_offset;
                }
                None => {
                    break;
                }
            }

            match self.newline_or_gap(offset) {
                Some((matched, new_offset)) => {
                    last_newline_or_gap = Some(matched);
                    if new_offset == offset {
                        break;
                    }
                    offset = new_offset;
                }
                None => {
                    return Ok((result, None, offset));
                }
            }
        }

        Ok((result, None, offset))
    }

    fn block_t(
        &self,
        start_node: &Command,
        end_command: &BlockCommand,
        offset: usize,
    ) -> Result<(FileElement, usize), Error> {
        let (body, end_command, offset) = self.block_body(end_command, offset)?;
        match end_command {
            None => Err(self.unbalanced_block(offset)),
            Some(end) => Ok((
                FileElement::Block {
                    start: start_node.clone(),
                    body,
                    end,
                },
                offset,
            )),
        }
    }

    fn block(&self, start_node: Command, offset: usize) -> Result<(FileElement, usize), Error> {
        let start_node_name = start_node.command_name().to_lowercase();
        if let Some((_, block_end)) = self
            .blocks
            .iter()
            .find(|(block_start, _)| block_start.as_str() == start_node_name)
        {
            return self.block_t(&start_node, block_end, offset);
        }

        let start_node = match start_node {
            Command::Element {
                command_invocation,
                line_comment: None,
            } => Command::Invocation(command_invocation),
            _ => start_node,
        };

        Ok((FileElement::Command(start_node), offset))
    }

    fn commented_argument_atom(
        &self,
        offset: usize,
    ) -> Result<Option<(CommentedArgumentComment, usize)>, Error> {
        if let Some((matched, offset)) = self.bracket_comment(offset)? {
            return Ok(Some((
                CommentedArgumentComment::BracketComment(matched),
                offset,
            )));
        }

        if let Some((comment, offset)) = self.line_comment(offset) {
            if let Some((newline, offset)) = self.newline(offset) {
                return Ok(Some((
                    CommentedArgumentComment::LineComment { comment, newline },
                    offset,
                )));
            }
        }

        Ok(None)
    }

    fn quotation_mark(&self, offset: usize) -> Option<usize> {
        if self.text[offset..].starts_with('"') {
            Some(offset + 1)
        } else {
            None
        }
    }

    fn quoted_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Argument, usize)>, Error> {
        static PATTERN: LazyLock<String> =
            LazyLock::new(|| format!("^{}", quoted_argument_pattern()));
        static RE: LazyLock<Regex> = LazyLock::new(|| regex(PATTERN.as_str()));
        match RE.find(&self.text[offset..]) {
            None => match self.quotation_mark(offset) {
                None => Ok(None),
                Some(_) => Err(self.generic_parsing_error(offset)),
            },
            Some(matched) => Ok(Some((
                Argument::Quoted {
                    value: {
                        let result = matched.as_str();
                        result[1..result.len() - 1].to_string()
                    },
                    position: {
                        if compute_position {
                            Some(self.position(offset))
                        } else {
                            None
                        }
                    },
                },
                self.skip_space(offset + matched.len()),
            ))),
        }
    }

    fn unquoted_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Option<(Argument, usize)> {
        static RE: LazyLock<Regex> = LazyLock::new(|| regex(unquoted_argument_pattern()));
        RE.find(&self.text[offset..]).map(|matched| {
            (
                Argument::Unquoted {
                    value: matched.as_str().to_string(),
                    position: {
                        if compute_position {
                            Some(self.position(offset))
                        } else {
                            None
                        }
                    },
                },
                self.skip_space(offset + matched.len()),
            )
        })
    }

    fn complex_argument(&self, offset: usize) -> Result<Option<(Argument, usize)>, Error> {
        Ok(match self.left_paren(offset) {
            None => None,
            Some(offset) => match self.arguments(offset, false)? {
                None => None,
                Some((matched_arguments, offset)) => {
                    let offset = self.right_paren(offset)?;
                    Some((
                        Argument::Complex {
                            arguments: matched_arguments,
                        },
                        offset,
                    ))
                }
            },
        })
    }

    fn argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Argument, usize)>, Error> {
        if let Some(matched) = self.bracket_argument(offset, compute_position)? {
            return Ok(Some(matched));
        }

        if let Some(matched) = self.quoted_argument(offset, compute_position)? {
            return Ok(Some(matched));
        }

        if let Some(matched) = self.unquoted_argument(offset, compute_position) {
            return Ok(Some(matched));
        }

        self.complex_argument(offset)
    }

    fn commented_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(ArgumentsAtom, usize)>, Error> {
        Ok(match self.argument(offset, compute_position)? {
            None => None,
            Some((matched_argument, offset)) => match self.commented_argument_atom(offset)? {
                None => Some((ArgumentsAtom::Argument(matched_argument), offset)),
                Some((nodes, offset)) => Some((
                    ArgumentsAtom::CommentedArgument {
                        argument: matched_argument,
                        comment: nodes,
                    },
                    offset,
                )),
            },
        })
    }

    fn separation(&self, offset: usize) -> Result<Option<(Option<ArgumentsAtom>, usize)>, Error> {
        if let Some((node, offset)) = self.bracket_comment(offset)? {
            return Ok(Some((Some(ArgumentsAtom::BracketComment(node)), offset)));
        }

        if let Some((node, offset)) = self.line_comment(offset) {
            return Ok(Some((Some(ArgumentsAtom::LineComment(node)), offset)));
        }

        if let Some((_, offset)) = self.newline(offset) {
            return Ok(Some((None, offset)));
        }

        Ok(None)
    }

    fn arguments_atom(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Option<ArgumentsAtom>, usize)>, Error> {
        if let Some((node, offset)) = self.commented_argument(offset, compute_position)? {
            return Ok(Some((Some(node), offset)));
        }

        if let Some(matched) = self.separation(offset)? {
            return Ok(Some(matched));
        }

        Ok(None)
    }

    fn arguments(
        &self,
        mut offset: usize,
        compute_position: bool,
    ) -> Result<Option<(ArgumentsNode, usize)>, Error> {
        let mut result = ArgumentsNode::new();
        while let Some((matched, new_offset)) = self.arguments_atom(offset, compute_position)? {
            if let Some(matched) = matched {
                result.push(matched);
            }
            offset = new_offset;
        }
        Ok(Some((result, offset)))
    }

    fn indentation(&self, offset: usize) -> String {
        let start = match self.text[..offset].rfind('\n') {
            Some(value) => value + 1,
            None => 0usize,
        };
        self.text[start..offset].to_string()
    }

    fn formatted_node(&self, start: usize, end: usize) -> String {
        let value = if start >= end {
            ""
        } else {
            &self.text[start + 1..end]
        };
        value.to_string()
    }

    fn create_command_invocation_node(
        &self,
        identifier: String,
        arguments: ArgumentsNode,
        initial_offset: usize,
        custom_formatting_start: usize,
        custom_formatting_end: usize,
    ) -> CommandInvocation {
        {
            {
                if self.is_known_command(identifier.as_str()) {
                    CommandInvocation::KnownCommand {
                        identifier,
                        arguments,
                    }
                } else {
                    let line = self.line(initial_offset) + 1;
                    let column = self.column(initial_offset);
                    CommandInvocation::CustomCommand {
                        indentation: self.indentation(initial_offset),
                        identifier,
                        arguments,
                        formatted_node: self
                            .formatted_node(custom_formatting_start, custom_formatting_end),
                        position: Position { line, column },
                    }
                }
            }
        }
    }

    fn command_invocation_t(
        &self,
        re: &regex::Regex,
        offset: usize,
    ) -> Result<Option<(CommandInvocation, usize)>, Error> {
        let initial_offset = offset;
        Ok(match self.raw_terminal(re, offset) {
            None => None,
            Some((matched_identifier, identifier_offset)) => {
                match self.left_paren(identifier_offset) {
                    None => None,
                    Some(offset) => match self.arguments(
                        offset,
                        matches!(
                            matched_identifier.to_lowercase().as_str(),
                            "function" | "macro"
                        ),
                    )? {
                        None => None,
                        Some((matched_arguments, arguments_offset)) => {
                            let offset = self.right_paren(arguments_offset)?;
                            Some((
                                self.create_command_invocation_node(
                                    matched_identifier,
                                    matched_arguments,
                                    initial_offset,
                                    identifier_offset,
                                    arguments_offset,
                                ),
                                offset,
                            ))
                        }
                    },
                }
            }
        })
    }

    fn command_element_t(
        &self,
        re: &regex::Regex,
        offset: usize,
    ) -> Result<Option<(Command, usize)>, Error> {
        Ok(self
            .command_invocation_t(re, offset)?
            .map(|(command_invocation, offset)| {
                let (line_comment, offset) = match self.line_comment(offset) {
                    None => (None, offset),
                    Some((matched_comment, new_offset)) => (Some(matched_comment), new_offset),
                };
                (
                    Command::Element {
                        command_invocation,
                        line_comment,
                    },
                    offset,
                )
            }))
    }

    fn command_element(&self, offset: usize) -> Result<Option<(Command, usize)>, Error> {
        static RE: LazyLock<Regex> = LazyLock::new(|| regex(IDENTIFIER_R));
        self.command_element_t(&RE, offset)
    }

    fn standalone_identifier(&self, offset: usize) -> Option<(FileElement, usize)> {
        static RE: LazyLock<Regex> = LazyLock::new(|| regex(IDENTIFIER_R));
        self.raw_terminal(&RE, offset).map(|(matched, new_offset)| {
            (
                FileElement::StandaloneIdentifier { value: matched },
                new_offset,
            )
        })
    }

    fn bracket_comment(&self, mut offset: usize) -> Result<Option<(BracketComment, usize)>, Error> {
        if let Some(new_offset) = self.pound_sign(offset) {
            offset = new_offset;
        } else {
            return Ok(None);
        }

        if let Some((Argument::Bracket(arg), new_offset)) = self.bracket_argument(offset, false)? {
            offset = new_offset;
            return Ok(Some((
                BracketComment {
                    value: arg.flatten(),
                },
                offset,
            )));
        }

        Ok(None)
    }

    fn line_comment(&self, offset: usize) -> Option<(LineComment, usize)> {
        self.pound_sign(offset).map(|offset| {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^[^\n]+"));
            match RE.find(&self.text[offset..]) {
                None => (
                    LineComment {
                        value: String::new(),
                    },
                    offset,
                ),
                Some(content) => (
                    LineComment {
                        value: content.as_str().to_string(),
                    },
                    offset + content.len(),
                ),
            }
        })
    }

    fn non_command_element(
        &self,
        mut offset: usize,
    ) -> Result<Option<(FileElement, usize)>, Error> {
        let mut bracket_comments = Vec::<BracketComment>::new();
        while let Some((matched, new_offset)) = self.bracket_comment(offset)? {
            bracket_comments.push(matched);
            offset = new_offset;
        }

        match self.line_comment(offset) {
            None => {
                if bracket_comments.is_empty() {
                    Ok(None)
                } else {
                    Ok(Some((
                        FileElement::NonCommandElement {
                            bracket_comments,
                            line_comment: None,
                        },
                        offset,
                    )))
                }
            }
            Some((matched, new_offset)) => Ok(Some((
                FileElement::NonCommandElement {
                    bracket_comments,
                    line_comment: Some(matched),
                },
                new_offset,
            ))),
        }
    }

    fn file_element(&self, offset: usize) -> Result<Option<(FileElement, usize)>, Error> {
        if let Some((result, offset)) = self.command_element(offset)? {
            return Ok(Some(self.block(result, offset)?));
        }

        if let Some(result) = self.standalone_identifier(offset) {
            return Ok(Some(result));
        }

        if let Some(result) = self.non_command_element(offset)? {
            return Ok(Some(result));
        }

        Ok(None)
    }

    fn newline_or_gap(&self, offset: usize) -> Option<(FileElement, usize)> {
        static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^(\n[ \t]*)(\n[ \t]*)*"));
        match RE.captures(&self.text[offset..]) {
            None => None,
            Some(captures) => match captures.get(2) {
                None => Some((
                    FileElement::NewlineOrGap {
                        value: "\n".to_string(),
                    },
                    offset + captures.get_match().len(),
                )),
                Some(_) => Some((
                    FileElement::NewlineOrGap {
                        value: "\n\n".to_string(),
                    },
                    offset + captures.get_match().len(),
                )),
            },
        }
    }

    pub fn start(&self) -> Result<Start, Error> {
        let mut offset = match self.newline_or_gap(0) {
            Some((_, new_offset)) => new_offset,
            None => 0usize,
        };
        let mut result: Vec<FileElement> = vec![];
        let mut last_newline_or_gap: Option<FileElement> = None;

        #[allow(clippy::while_let_loop)]
        loop {
            match self.file_element(offset)? {
                Some((matched, new_offset)) => {
                    if let Some(node) = last_newline_or_gap {
                        result.push(node);
                    }
                    result.push(matched);
                    if new_offset == offset {
                        break;
                    }
                    offset = new_offset;
                }
                None => {
                    break;
                }
            }

            match self.newline_or_gap(offset) {
                Some((matched, new_offset)) => {
                    last_newline_or_gap = Some(matched);
                    if new_offset == offset {
                        break;
                    }
                    offset = new_offset;
                }
                None => {
                    break;
                }
            }
        }

        if offset != self.text.len() {
            let offset = self.right_paren(offset)?;
            return Err(self.unbalanced_parentheses(offset));
        }

        Ok(Start { children: result })
    }

    fn is_known_command(&self, command_name: &str) -> bool {
        let command_name = command_name.to_lowercase();
        self.schemas.contains_key(&command_name)
    }
}

fn block_command(name: &str) -> BlockCommand {
    let pattern = format!("(?i)^({name})[ \t]*");
    let re = regex(pattern.as_str());
    BlockCommand { re }
}

fn prepare_blocks(schemas: &CommandSchemas) -> Vec<(String, BlockCommand)> {
    schemas
        .values()
        .filter_map(|schema| match schema {
            CommandSchema {
                canonical_name: Some(canonical_name),
                block_end: Some(block_end),
                ..
            } => Some((
                canonical_name.trim().to_lowercase(),
                block_command(block_end),
            )),
            _ => None,
        })
        .collect()
}

pyo3::import_exception!(gersemi.exceptions, GenericParsingError);
pyo3::import_exception!(gersemi.exceptions, UnbalancedBlock);
pyo3::import_exception!(gersemi.exceptions, UnbalancedBrackets);
pyo3::import_exception!(gersemi.exceptions, UnbalancedParentheses);

impl From<Error> for PyErr {
    fn from(error: Error) -> Self {
        let exception = match error.error_type {
            ErrorType::GenericParsingError => GenericParsingError::new_err,
            ErrorType::UnbalancedBlock => UnbalancedBlock::new_err,
            ErrorType::UnbalancedBrackets => UnbalancedBrackets::new_err,
            ErrorType::UnbalancedParentheses => UnbalancedParentheses::new_err,
        };
        exception((error.explanation, error.line, error.column))
    }
}
