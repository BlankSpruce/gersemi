use crate::argument_schema::{BlockCommand, CommandSchemas};
use crate::configuration::{KeywordFormatter, KeywordPreprocessor};
use crate::node::{
    Argument, ArgumentsAtom, ArgumentsNode, BracketArgument, BracketComment, Command,
    CommandInvocation, CommentedArgumentComment, FileElement, InlineHintKind, LineComment,
    Position, Start,
};
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use regex::Regex;
use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

pub struct Parser<'a> {
    text: &'a str,
    line_offsets: Vec<usize>,
    blocks: &'a Vec<(String, BlockCommand)>,
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

pub fn re_find<'a>(pattern: &str, s: &'a str) -> Option<regex::Match<'a>> {
    static REGEXES: LazyLock<Mutex<HashMap<String, Regex>>> =
        LazyLock::new(|| Mutex::new(HashMap::<String, Regex>::new()));

    let mut regexes = REGEXES.lock().unwrap();
    match regexes.get(pattern) {
        None => {
            let re = Regex::new(pattern).unwrap();
            let result = re.find(s);
            regexes.insert(pattern.to_string(), re);
            result
        }
        Some(re) => re.find(s),
    }
}

pub fn is_case_insensitive_match(pattern: &str, s: &str) -> bool {
    (pattern == s) || (pattern == s.to_lowercase())
}

pub fn is_function_or_macro(s: &str) -> bool {
    matches!(s, "function" | "macro")
        || (s.starts_with(['F', 'M']) && matches!(s.to_lowercase().as_str(), "function" | "macro"))
}

fn inline_hint(value: &str, offset: usize) -> Option<(Argument<'_>, usize)> {
    let hint = value.strip_prefix("[[gersemi: ")?;
    let hint = hint.strip_suffix("]]")?;

    let kind = if let Some(hint) = KeywordPreprocessor::from_str(hint) {
        InlineHintKind::KeywordPreprocessor(hint)
    } else if let Some(hint) = KeywordFormatter::from_str(hint) {
        InlineHintKind::KeywordFormatter(hint)
    } else {
        let hint = hint.strip_prefix("as_command=")?;
        InlineHintKind::AsCommand {
            command: hint.to_lowercase(),
        }
    };

    Some((Argument::InlineHint { value, kind }, offset))
}

enum BlockEndNode<'a> {
    Yes(Command<'a>),
    No(FileElement<'a>),
}

fn get_block_end<'a>(pattern: &str, element: FileElement<'a>) -> BlockEndNode<'a> {
    match element {
        FileElement::Command(command) => match command {
            Command::Element {
                ref command_invocation,
                ..
            }
            | Command::Invocation(ref command_invocation) => match command_invocation {
                CommandInvocation::KnownCommand { identifier, .. }
                    if is_case_insensitive_match(pattern, identifier) =>
                {
                    BlockEndNode::Yes(command)
                }
                CommandInvocation::CustomCommand { identifier, .. }
                    if is_case_insensitive_match(pattern, identifier) =>
                {
                    BlockEndNode::Yes(command)
                }
                _ => BlockEndNode::No(FileElement::Command(command)),
            },
        },
        _ => BlockEndNode::No(element),
    }
}

impl Parser<'_> {
    pub fn new<'a>(text: &'a str, schemas: &'a CommandSchemas) -> Parser<'a> {
        let line_offsets = text
            .chars()
            .enumerate()
            .filter(|(_, c)| *c == '\n')
            .map(|(i, _)| i)
            .collect::<Vec<_>>();
        Parser {
            text,
            line_offsets,
            blocks: &schemas.blocks,
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
        start_offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Argument<'_>, usize)>, Error> {
        static RE_START: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^\[=*\[").unwrap());
        match RE_START.find(&self.text[start_offset..]) {
            None => Ok(None),
            Some(matched_left_bracket) => {
                let edge = matched_left_bracket.len();
                let bracket_width = edge - 2;
                let re_pattern = format!(r"]{}]", "=".repeat(bracket_width));
                let offset = start_offset + edge;
                match self.text[offset..].find(&re_pattern) {
                    None => Err(self.unbalanced_brackets(offset)),
                    Some(value) => Ok(Some((
                        Argument::Bracket(BracketArgument {
                            value: &self.text[offset..][..value],
                            whole: &self.text[start_offset..][..value + 2 * edge],
                            position: {
                                if compute_position {
                                    Some(self.position(offset))
                                } else {
                                    None
                                }
                            },
                        }),
                        self.skip_space(offset + value + edge),
                    ))),
                }
            }
        }
    }

    fn raw_identifier(&self, offset: usize) -> Option<(&str, usize)> {
        let mut characters = self.text[offset..].chars();
        let mut new_offset = match characters.next() {
            Some('a'..='z' | 'A'..='Z' | '_' | '@') => offset + 1,
            _ => {
                return None;
            }
        };

        for c in characters {
            match c {
                'a'..='z' | 'A'..='Z' | '_' | '@' | '0'..='9' => {
                    new_offset += 1;
                }
                _ => {
                    break;
                }
            }
        }
        Some((&self.text[offset..new_offset], new_offset))
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

    fn newline(&self, offset: usize) -> Option<usize> {
        let mut result = offset;
        while self.text[result..].starts_with('\n') {
            result += 1;
        }

        if result == offset {
            return None;
        }

        Some(self.skip_space(result))
    }

    fn block_body(
        &self,
        end_command: &BlockCommand,
        mut offset: usize,
    ) -> Result<(Vec<FileElement<'_>>, Option<Command<'_>>, usize), Error> {
        if let Some((_, new_offset)) = self.newline_or_gap(offset) {
            offset = new_offset;
        }

        let mut result: Vec<FileElement> = vec![];
        let mut last_newline_or_gap: Option<FileElement> = None;

        #[allow(clippy::while_let_loop)]
        loop {
            match self.file_element(offset)? {
                Some((matched, new_offset)) => {
                    let matched = match get_block_end(&end_command.pattern, matched) {
                        BlockEndNode::No(matched) => matched,
                        BlockEndNode::Yes(end_command) => {
                            return Ok((result, Some(end_command), new_offset));
                        }
                    };
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

    fn block_t<'a>(
        &'a self,
        start_node: Command<'a>,
        end_command: &BlockCommand,
        offset: usize,
    ) -> Result<(FileElement<'a>, usize), Error> {
        let (body, end_command, offset) = self.block_body(end_command, offset)?;
        match end_command {
            None => Err(self.unbalanced_block(offset)),
            Some(end) => Ok((
                FileElement::Block {
                    start: start_node,
                    body,
                    end,
                },
                offset,
            )),
        }
    }

    fn block<'a>(
        &'a self,
        start_node: Command<'a>,
        offset: usize,
    ) -> Result<(FileElement<'a>, usize), Error> {
        let start_node_name = start_node.command_name().to_lowercase();
        if let Some((_, block_end)) = self
            .blocks
            .iter()
            .find(|(block_start, _)| block_start.as_str() == start_node_name)
        {
            return self.block_t(start_node, block_end, offset);
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
    ) -> Result<Option<(CommentedArgumentComment<'_>, usize)>, Error> {
        if !self.text[offset..].starts_with('#') {
            return Ok(None);
        }

        if let Some((matched, offset)) = self.bracket_comment(offset)? {
            if inline_hint(matched.value, offset).is_some() {
                return Ok(None);
            }

            return Ok(Some((
                CommentedArgumentComment::BracketComment(matched),
                offset,
            )));
        }

        if let Some((comment, offset)) = self.line_comment(offset) {
            if let Some(offset) = self.newline(offset) {
                return Ok(Some((
                    CommentedArgumentComment::LineComment(comment),
                    offset,
                )));
            }
        }

        Ok(None)
    }

    fn quoted_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Argument<'_>, usize)>, Error> {
        let mut characters = self.text[offset..].chars();
        let mut new_offset = if characters.next() == Some('"') {
            offset + 1
        } else {
            return Err(self.generic_parsing_error(offset));
        };

        while let Some(c) = characters.next() {
            match c {
                '"' => {
                    new_offset += 1;
                    return Ok(Some((
                        Argument::Quoted {
                            value: &self.text[offset + 1..new_offset - 1],
                            position: {
                                if compute_position {
                                    Some(self.position(offset))
                                } else {
                                    None
                                }
                            },
                        },
                        self.skip_space(new_offset),
                    )));
                }
                '\\' => {
                    let Some(c2) = characters.next() else {
                        break;
                    };
                    match c2 {
                        'n' | 'r' | 't' => {}
                        'A'..='Z' | 'a'..='z' | '0'..='9' => {
                            break;
                        }
                        _ => {}
                    }
                    new_offset += 1 + c.len_utf8();
                }
                _ => {
                    new_offset += c.len_utf8();
                }
            }
        }

        Err(self.generic_parsing_error(offset))
    }

    fn unquoted_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Option<(Argument<'_>, usize)> {
        static RE: LazyLock<Regex> =
            LazyLock::new(|| Regex::new(unquoted_argument_pattern()).unwrap());
        RE.find(&self.text[offset..]).map(|matched| {
            (
                Argument::Unquoted {
                    value: matched.as_str(),
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

    fn complex_argument(&self, offset: usize) -> Result<Option<(Argument<'_>, usize)>, Error> {
        Ok(match self.left_paren(offset) {
            None => None,
            Some(offset) => match self.arguments(offset, false)? {
                None => None,
                Some((matched_arguments, offset)) => {
                    let offset = self.right_paren(offset)?;
                    let as_value = matched_arguments
                        .iter()
                        .filter_map(|x| match x {
                            ArgumentsAtom::Argument(node)
                            | ArgumentsAtom::CommentedArgument { argument: node, .. } => {
                                Some(node.get_value())
                            }
                            ArgumentsAtom::BracketComment(_) | ArgumentsAtom::LineComment(_) => {
                                None
                            }
                        })
                        .collect::<Vec<_>>()
                        .join(" ");

                    Some((
                        Argument::Complex {
                            arguments: matched_arguments,
                            as_value,
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
    ) -> Result<Option<(Argument<'_>, usize)>, Error> {
        if self.text[offset..].is_empty() {
            return Ok(None);
        }

        Ok(match &self.text[offset..][..1] {
            "#" => {
                if let Some((BracketComment { value }, offset)) = self.bracket_comment(offset)? {
                    inline_hint(value, offset)
                } else {
                    None
                }
            }
            "\"" => self.quoted_argument(offset, compute_position)?,
            "(" => self.complex_argument(offset)?,
            _ => {
                if self.text[offset..].starts_with("[[") || self.text[offset..].starts_with("[=") {
                    self.bracket_argument(offset, compute_position)?
                } else {
                    self.unquoted_argument(offset, compute_position)
                }
            }
        })
    }

    fn commented_argument(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(ArgumentsAtom<'_>, usize)>, Error> {
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

    fn separation(
        &self,
        offset: usize,
    ) -> Result<Option<(Option<ArgumentsAtom<'_>>, usize)>, Error> {
        if self.text[offset..].starts_with('#') {
            if let Some((node, offset)) = self.bracket_comment(offset)? {
                return Ok(Some((Some(ArgumentsAtom::BracketComment(node)), offset)));
            }

            if let Some((node, offset)) = self.line_comment(offset) {
                return Ok(Some((Some(ArgumentsAtom::LineComment(node)), offset)));
            }
        }

        if let Some(offset) = self.newline(offset) {
            return Ok(Some((None, offset)));
        }

        Ok(None)
    }

    fn arguments_atom(
        &self,
        offset: usize,
        compute_position: bool,
    ) -> Result<Option<(Option<ArgumentsAtom<'_>>, usize)>, Error> {
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
    ) -> Result<Option<(ArgumentsNode<'_>, usize)>, Error> {
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

    fn formatted_node(&self, start: usize, end: usize) -> &str {
        if start >= end {
            ""
        } else {
            &self.text[start + 1..end]
        }
    }

    fn create_command_invocation_node<'a>(
        &'a self,
        identifier: String,
        arguments: ArgumentsNode<'a>,
        initial_offset: usize,
        custom_formatting_start: usize,
        custom_formatting_end: usize,
    ) -> CommandInvocation<'a> {
        {
            {
                if self.schemas.contains_key(&identifier) {
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

    fn command_invocation(
        &self,
        offset: usize,
    ) -> Result<Option<(CommandInvocation<'_>, usize)>, Error> {
        let initial_offset = offset;
        Ok(match self.raw_identifier(offset) {
            None => None,
            Some((matched_identifier, identifier_offset)) => {
                let identifier_offset = self.skip_space(identifier_offset);
                match self.left_paren(identifier_offset) {
                    None => None,
                    Some(offset) => {
                        match self.arguments(offset, is_function_or_macro(matched_identifier))? {
                            None => None,
                            Some((matched_arguments, arguments_offset)) => {
                                let offset = self.right_paren(arguments_offset)?;
                                Some((
                                    self.create_command_invocation_node(
                                        matched_identifier.to_string(),
                                        matched_arguments,
                                        initial_offset,
                                        identifier_offset,
                                        arguments_offset,
                                    ),
                                    offset,
                                ))
                            }
                        }
                    }
                }
            }
        })
    }

    fn command_element(&self, offset: usize) -> Result<Option<(Command<'_>, usize)>, Error> {
        Ok(self
            .command_invocation(offset)?
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

    fn standalone_identifier(&self, offset: usize) -> Option<(FileElement<'_>, usize)> {
        self.raw_identifier(offset).map(|(matched, new_offset)| {
            (
                FileElement::StandaloneIdentifier { value: matched },
                self.skip_space(new_offset),
            )
        })
    }

    fn bracket_comment(
        &self,
        mut offset: usize,
    ) -> Result<Option<(BracketComment<'_>, usize)>, Error> {
        if let Some(new_offset) = self.pound_sign(offset) {
            offset = new_offset;
        } else {
            return Ok(None);
        }

        if let Some((Argument::Bracket(arg), new_offset)) = self.bracket_argument(offset, false)? {
            offset = new_offset;
            return Ok(Some((BracketComment { value: arg.whole }, offset)));
        }

        Ok(None)
    }

    fn line_comment(&self, offset: usize) -> Option<(LineComment<'_>, usize)> {
        self.pound_sign(offset).map(|offset| {
            let value = match self.text[offset..].find('\n') {
                None => &self.text[offset..],
                Some(end) => &self.text[offset..][..end],
            };

            (LineComment { value }, offset + value.len())
        })
    }

    fn non_command_element(
        &self,
        mut offset: usize,
    ) -> Result<Option<(FileElement<'_>, usize)>, Error> {
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

    fn file_element(&self, offset: usize) -> Result<Option<(FileElement<'_>, usize)>, Error> {
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

    fn newline_or_gap(&self, offset: usize) -> Option<(FileElement<'_>, usize)> {
        if !self.text[offset..].starts_with('\n') {
            return None;
        }
        let offset_after_first_nl = self.skip_space(offset + 1);

        let mut offset = offset_after_first_nl;
        while self.text[offset..].starts_with('\n') {
            offset = self.skip_space(offset + 1);
        }

        Some((
            FileElement::NewlineOrGap {
                value: if offset == offset_after_first_nl {
                    "\n"
                } else {
                    "\n\n"
                },
            },
            offset,
        ))
    }

    pub fn start(&self) -> Result<Start<'_>, Error> {
        let offset = match self.newline_or_gap(0) {
            Some((_, new_offset)) => new_offset,
            None => 0usize,
        };
        let mut offset = self.skip_space(offset);
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
}

impl From<Error> for PyErr {
    fn from(error: Error) -> Self {
        let description = match error.error_type {
            ErrorType::GenericParsingError => "unspecified parsing error",
            ErrorType::UnbalancedBlock => "unbalanced block",
            ErrorType::UnbalancedBrackets => "unbalanced brackets",
            ErrorType::UnbalancedParentheses => "unbalanced parentheses",
        };
        PyRuntimeError::new_err(format!(
            "{}:{}: {description}\n{}",
            error.line, error.column, error.explanation
        ))
    }
}
