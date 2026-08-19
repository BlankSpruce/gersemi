use crate::argument_schema::{
    is_one_of_keywords, single_word_matchers, ArgumentSchema, CommandSchema, CommandSchemaDetails,
    CommandSchemaMapping, CommandSchemas, KeywordMatcher, Signatures,
};
use crate::configuration::{
    Configuration, IndentType, KeywordFormatter, KeywordPreprocessor, LineRange, ListExpansion,
    OutcomeConfiguration, SortOrder,
};
use crate::custom_command_definition_finder::{
    find_all_custom_command_definitions, CustomCommand, CustomCommandContent, Keywords,
};
use crate::keyword_preprocessor::{
    keep_unique_arguments, sort_and_keep_unique_arguments, sort_arguments,
};
use crate::node::{
    Argument, ArgumentsAtom, ArgumentsNode, BracketComment, Command, CommandInvocation,
    CommentedArgumentComment, FileElement, InlineHintKind, LineComment, Position,
    RefinedArgumentsAtom, RefinedArgumentsNode, Start,
};
use crate::parser::{quoted_argument_pattern, re_find, Parser};
use crate::sanity_checker::check_equivalence;
use crate::utils::load_definitions_from_extensions;
use pyo3::exceptions::PyRuntimeError;
use pyo3::{pyclass, pymethods, PyErr, PyResult, Python};
use regex::Regex;
use rust_yaml::{Value, Yaml};
use std::borrow::Cow;
use std::cell::RefCell;
use std::collections::HashMap;
use std::iter::zip;
use std::str::SplitInclusive;
use std::sync::LazyLock;

pub type UnknownCommandsUsed = Vec<(String, usize, usize)>;

#[derive(Clone)]
struct FormatterImpl<'a> {
    active_schema: Option<&'a ArgumentSchema>,
    active_command: Option<&'a CommandSchema>,
    favour_expansion: bool,
    indent_symbol: Cow<'a, str>,

    unknown_commands_used: &'a RefCell<UnknownCommandsUsed>,

    configuration: &'a OutcomeConfiguration,
    schemas: &'a CommandSchemas,
}

fn remove_common_beginning(s: &str, other: &str) -> String {
    let mut index = 0;
    for (lhs, rhs) in zip(s.chars(), other.chars()) {
        if lhs != rhs {
            break;
        }
        index += 1;
    }

    s[index..].to_string()
}

fn strip_empty_lines_from_edges(s: &str) -> String {
    let mut result = s
        .lines()
        .skip_while(|x| x.trim().is_empty())
        .collect::<Vec<&str>>()
        .into_iter()
        .rev()
        .skip_while(|x| x.trim().is_empty())
        .collect::<Vec<&str>>();
    result.reverse();
    result.join("\n")
}

fn ends_with_line_comment(s: &str) -> bool {
    let mut start = 0;
    loop {
        let line_comment_begin_index = s[start..].rfind('#');
        match line_comment_begin_index {
            None => {
                return false;
            }
            Some(index) => {
                let bracket_comment_begin_index = s[start..].rfind("#[");
                if bracket_comment_begin_index == Some(index) {
                    start = index + 1;
                } else {
                    return true;
                }
            }
        }
    }
}

fn flat_split(pattern: &str, s: &str) -> (String, Option<[String; 2]>) {
    match re_find(pattern, s) {
        None => (s.to_string(), None),
        Some(m) => (
            s[..m.start()].to_string(),
            Some([s[m.range()].to_string(), s[m.end()..].to_string()]),
        ),
    }
}

fn split_by_line_comment(s: &str) -> (String, Option<[String; 2]>) {
    flat_split(r"\s*#", s)
}

fn split_by_bracket_arguments(s: &str) -> (String, Option<[String; 2]>) {
    static REGEX_START: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\[(=*)\[").unwrap());
    if let Some(left_bracket) = REGEX_START.find(s) {
        let equal_signs = "=".repeat(left_bracket.len() - 2);
        let pattern = format!(r"\[{equal_signs}\[([\s\S]+?)\]{equal_signs}\]");
        return flat_split(&pattern, s);
    }

    (s.to_string(), None)
}

fn split_by_quoted_arguments(s: &String) -> Vec<String> {
    static RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(quoted_argument_pattern()).unwrap());
    let mut s: &str = s;
    let mut result = Vec::<String>::new();
    while let Some(matched) = RE.find(s) {
        result.push(s[..matched.start()].to_string());
        result.push(s[matched.range()].to_string());
        s = &s[matched.end()..];
    }
    result.push(s.to_string());
    result
}

fn split_into_segments(s: &str) -> Vec<String> {
    let (head, comment) = split_by_line_comment(s);
    let line_comment = match comment {
        None => String::new(),
        Some(comment) => comment.into_iter().collect::<String>(),
    };

    let (head, line_comment) = if head.contains('"') {
        (format!("{head}{line_comment}"), String::new())
    } else {
        (head, line_comment)
    };

    let segments = split_by_bracket_arguments(&head);
    let segments = match segments {
        (front, None) => vec![split_by_quoted_arguments(&front), vec![line_comment]],
        (front, Some([middle, back])) => vec![
            split_by_quoted_arguments(&front),
            split_by_quoted_arguments(&middle),
            split_by_quoted_arguments(&back),
            vec![line_comment],
        ],
    };

    let mut result = Vec::<String>::new();
    for segment in segments {
        for item in segment {
            if !item.is_empty() {
                result.push(item);
            }
        }
    }
    result
}

fn indent<Predicate: Fn(&str) -> bool>(
    s: &str,
    indent_symbol: &str,
    predicate: Predicate,
) -> String {
    let mut buffer = String::new();
    for line in s.split_inclusive('\n') {
        if predicate(line) {
            buffer.push_str(indent_symbol);
        }
        buffer.push_str(line);
    }
    buffer
}

fn indent_segment(segment: &str, indent_symbol: &str) -> String {
    if segment.starts_with('[')
        || segment.starts_with('"')
        || segment.starts_with(' ')
        || segment.starts_with('\t')
    {
        return segment.to_string();
    }

    indent(segment, indent_symbol, |x| !x.starts_with('\n'))
}

fn safe_indent(s: &str, indent_symbol: &str) -> String {
    split_into_segments(s)
        .into_iter()
        .map(|x| indent_segment(&x, indent_symbol))
        .collect::<String>()
}

trait HasLineComment {
    fn has_line_comment(&self) -> bool;
}

impl HasLineComment for ArgumentsAtom<'_> {
    fn has_line_comment(&self) -> bool {
        match self {
            Self::Argument(_) | Self::BracketComment(_) => false,
            Self::LineComment(_) => true,
            Self::CommentedArgument { comment, .. } => match comment {
                CommentedArgumentComment::BracketComment(_) => false,
                CommentedArgumentComment::LineComment { .. } => true,
            },
        }
    }
}

impl<T: HasLineComment> HasLineComment for Vec<T> {
    fn has_line_comment(&self) -> bool {
        self.iter().any(HasLineComment::has_line_comment)
    }
}

impl HasLineComment for RefinedArgumentsAtom<'_> {
    fn has_line_comment(&self) -> bool {
        (&self).has_line_comment()
    }
}

impl HasLineComment for &RefinedArgumentsAtom<'_> {
    fn has_line_comment(&self) -> bool {
        match self {
            RefinedArgumentsAtom::Atom(atom) => atom.has_line_comment(),
            RefinedArgumentsAtom::BinaryOperation {
                lhs,
                operation,
                rhs,
            } => lhs.has_line_comment() || operation.has_line_comment() || rhs.has_line_comment(),
            RefinedArgumentsAtom::UnaryOperation { operation, operand } => {
                operation.has_line_comment()
                    || operand
                        .as_deref()
                        .is_some_and(HasLineComment::has_line_comment)
            }
            RefinedArgumentsAtom::OptionArgument { keyword } => keyword.has_line_comment(),
            RefinedArgumentsAtom::OneValueArgument {
                keyword: first,
                arguments: rest,
            }
            | RefinedArgumentsAtom::MultiValueArgument {
                keyword: first,
                arguments: rest,
            }
            | RefinedArgumentsAtom::Section {
                header: first,
                values: rest,
            }
            | RefinedArgumentsAtom::Pair { first, rest } => {
                first.has_line_comment() || rest.has_line_comment()
            }
            RefinedArgumentsAtom::PositionalArguments(args) => args.has_line_comment(),
            RefinedArgumentsAtom::KeywordArgument {
                first,
                in_between,
                second,
            } => {
                first.has_line_comment()
                    || in_between.has_line_comment()
                    || second.has_line_comment()
            }
        }
    }
}

impl HasLineComment for &&str {
    fn has_line_comment(&self) -> bool {
        true
    }
}

trait TryToFormatIntoSingleLinePart {
    fn format_into_buffer(&self, formatter: &mut FormatterImpl, buffer: &mut String);
}

impl TryToFormatIntoSingleLinePart for ArgumentsAtom<'_> {
    fn format_into_buffer(&self, formatter: &mut FormatterImpl, buffer: &mut String) {
        let x = RefinedArgumentsAtom::Atom(self.clone());
        formatter.arguments_atom(&x, buffer);
    }
}

impl TryToFormatIntoSingleLinePart for RefinedArgumentsAtom<'_> {
    fn format_into_buffer(&self, formatter: &mut FormatterImpl, buffer: &mut String) {
        formatter.arguments_atom(self, buffer);
    }
}

impl TryToFormatIntoSingleLinePart for &RefinedArgumentsAtom<'_> {
    fn format_into_buffer(&self, formatter: &mut FormatterImpl, buffer: &mut String) {
        formatter.arguments_atom(self, buffer);
    }
}

impl TryToFormatIntoSingleLinePart for &&str {
    fn format_into_buffer(&self, _formatter: &mut FormatterImpl, buffer: &mut String) {
        buffer.push_str(self);
    }
}

fn is_line_comment_in_any_of(arguments: &RefinedArgumentsNode) -> bool {
    arguments.iter().any(HasLineComment::has_line_comment)
}

fn pair_arguments(arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
    let mut result = RefinedArgumentsNode::with_capacity(arguments.len() / 2 + 1);
    let mut accumulator = RefinedArgumentsNode::with_capacity(2);
    for argument in arguments {
        if accumulator.is_empty() {
            if argument.is_comment() {
                result.push(argument);
            } else {
                accumulator.push(argument);
            }
        } else {
            let is_comment_node = argument.is_comment();
            accumulator.push(argument);
            if !is_comment_node {
                let mut accumulator = std::mem::take(&mut accumulator);
                let rest = accumulator.split_off(1);
                result.push(RefinedArgumentsAtom::Pair {
                    first: Box::new(accumulator.pop().unwrap()),
                    rest,
                });
            }
        }
    }

    if !accumulator.is_empty() {
        let rest = accumulator.split_off(1);
        result.push(RefinedArgumentsAtom::Pair {
            first: Box::new(accumulator.pop().unwrap()),
            rest,
        });
    }

    result
}

fn line_comment_is_only_at_rightmost_edge<Part: HasLineComment>(
    parts: &[Part],
    postfix: &str,
) -> bool {
    if parts.is_empty() {
        return true;
    }

    let end_index = if postfix.is_empty() {
        parts.len() - 1
    } else {
        parts.len()
    };

    !parts
        .iter()
        .take(end_index)
        .any(HasLineComment::has_line_comment)
}

fn preprocess_content(content: &str) -> String {
    if content.trim().is_empty() {
        return String::new();
    }

    let begin = if content.starts_with('\n') { "\n" } else { "" };
    let stripped_content = strip_empty_lines_from_edges(content);
    if ends_with_line_comment(&stripped_content) {
        return format!("{begin}{stripped_content}\n");
    }

    let end = if content.ends_with('\n') { "\n" } else { "" };

    let stripped_content = stripped_content.trim_end();
    format!("{begin}{stripped_content}{end}")
}

impl FormatterImpl<'_> {
    fn not_indented(&self) -> Self {
        let mut result = self.clone();
        result.indent_symbol = Cow::from("");
        result
    }

    fn indented(&self) -> Self {
        let mut result = self.clone();
        result.indent_symbol = Cow::from(format!(
            "{}{}",
            self.configuration.indent_type.as_string(),
            self.indent_symbol
        ));
        result
    }

    fn dedented(&self) -> Self {
        let indent_type = self.configuration.indent_type.as_string();
        let mut result = self.clone();
        result.indent_symbol = self
            .indent_symbol
            .strip_prefix(&indent_type)
            .map_or_else(|| Cow::from(""), |x| Cow::from(x.to_string()));
        result
    }

    fn patch_active_command<'a>(
        &'a self,
        active_command: Option<&'a CommandSchema>,
    ) -> FormatterImpl<'a> {
        let mut result = self.clone();
        if let Some(active_command) = active_command {
            result.active_schema = match &active_command.details {
                CommandSchemaDetails::StandardCommand { schema, .. } => Some(schema),
                CommandSchemaDetails::SpecializedCommand { .. } => None,
            };
        }
        result.active_command = active_command;
        result
    }

    fn select_inlining_strategy(&self) -> Self {
        let mut result = self.clone();
        result.favour_expansion = false;
        result
    }

    fn select_expansion_strategy(&self) -> Self {
        let mut result = self.clone();
        result.favour_expansion = matches!(
            self.configuration.list_expansion,
            ListExpansion::FavourExpansion
        );
        result
    }

    fn block_body(&self, node: Vec<FileElement>, buffer: &mut String) {
        let f = self.indented();
        let has_nodes = !node.is_empty();
        for x in node {
            f.file_element(x, buffer);
        }

        if has_nodes {
            buffer.push('\n');
        }
    }

    fn two_words_keywords(&self) -> &Vec<KeywordMatcher> {
        static EMPTY: Vec<KeywordMatcher> = vec![];
        match self.active_command {
            Some(CommandSchema {
                details:
                    CommandSchemaDetails::StandardCommand {
                        ref two_words_keywords,
                        ..
                    },
                ..
            }) => two_words_keywords,
            _ => &EMPTY,
        }
    }

    fn standard_preprocess_arguments<'a>(
        &self,
        arguments: RefinedArgumentsNode<'a>,
    ) -> RefinedArgumentsNode<'a> {
        crate::two_words_keyword_isolator::preprocess_arguments(
            self.two_words_keywords(),
            arguments,
        )
    }

    fn preprocess_arguments<'a>(&self, arguments: ArgumentsNode<'a>) -> RefinedArgumentsNode<'a> {
        self.preprocess_refined_arguments(
            arguments
                .into_iter()
                .map(RefinedArgumentsAtom::Atom)
                .collect(),
        )
    }

    fn preprocess_refined_arguments<'a>(
        &self,
        arguments: RefinedArgumentsNode<'a>,
    ) -> RefinedArgumentsNode<'a> {
        if self.shall_use_condition_syntax() {
            crate::argument_schema::isolate_conditions(arguments)
        } else {
            self.standard_preprocess_arguments(arguments)
        }
    }

    fn signatures(&self) -> Option<&Signatures> {
        match self.active_command {
            Some(CommandSchema {
                details: CommandSchemaDetails::StandardCommand { ref signatures, .. },
                ..
            }) => Some(signatures),
            _ => None,
        }
    }

    fn get_signature_from_atom(&self, atom: &RefinedArgumentsAtom) -> Option<&ArgumentSchema> {
        let signatures = self.signatures()?;
        let value = atom.get_keyword_value();
        let value = value.as_ref();
        for (item, signature) in signatures {
            let Some(item) = item else {
                continue;
            };
            if is_one_of_keywords(value, std::slice::from_ref(item)) {
                return Some(signature);
            }
        }

        let fallback: Option<KeywordMatcher> = None;
        signatures.get(&fallback)
    }

    fn get_signature(&self, arguments: &RefinedArgumentsNode) -> Option<&ArgumentSchema> {
        for atom in arguments {
            if let Some(result) = self.get_signature_from_atom(atom) {
                return Some(result);
            }
        }
        None
    }

    fn standard_complex_argument(&self, arguments: &ArgumentsNode, buffer: &mut String) {
        if arguments.len() <= 4
            && self.try_to_format_into_single_line(&["("], arguments, ")", buffer)
        {
            return;
        }

        buffer.push_str(&self.indent_symbol);
        buffer.push_str("(\n");
        let arguments = arguments
            .iter()
            .map(|x| RefinedArgumentsAtom::Atom(x.clone()))
            .collect();
        self.indented().arguments(&arguments, buffer);
        buffer.push('\n');
        buffer.push_str(&self.indent_symbol);
        buffer.push(')');
    }

    fn condition_syntax_complex_argument(&self, arguments: &ArgumentsNode, buffer: &mut String) {
        let arguments = self.preprocess_arguments(arguments.clone());
        if self.try_to_format_into_single_line(&["("], &arguments, ")", buffer) {
            return;
        }

        buffer.push_str(&self.indent_symbol);
        buffer.push_str("(\n");
        self.indented().arguments(&arguments, buffer);
        buffer.push('\n');
        buffer.push_str(&self.indent_symbol);
        buffer.push(')');
    }

    fn shall_use_condition_syntax(&self) -> bool {
        match self.active_command {
            Some(CommandSchema {
                details:
                    CommandSchemaDetails::SpecializedCommand {
                        ref specialization, ..
                    },
                ..
            }) => matches!(
                specialization.as_str(),
                "condition_syntax_with_dedent" | "condition_syntax"
            ),
            _ => false,
        }
    }

    fn complex_argument(&self, arguments: &ArgumentsNode, buffer: &mut String) {
        if self.shall_use_condition_syntax() {
            self.condition_syntax_complex_argument(arguments, buffer);
        } else {
            self.standard_complex_argument(arguments, buffer);
        }
    }

    fn argument(&self, argument: &Argument, buffer: &mut String) {
        match argument {
            Argument::Bracket(arg) => {
                buffer.push_str(&self.indent_symbol);
                buffer.push_str(arg.whole);
            }
            Argument::Complex { arguments, .. } => {
                self.complex_argument(arguments, buffer);
            }
            Argument::Quoted { value, .. } => {
                buffer.push_str(&self.indent_symbol);
                buffer.push('"');
                buffer.push_str(value);
                buffer.push('"');
            }
            Argument::Unquoted { value, .. } => {
                buffer.push_str(&self.indent_symbol);
                buffer.push_str(value);
            }
            Argument::InlineHint { value, .. } => {
                buffer.push_str(&self.indent_symbol);
                buffer.push('#');
                buffer.push_str(value);
            }
        }
    }

    fn commented_argument(
        &self,
        argument: &Argument,
        comment: &CommentedArgumentComment,
        buffer: &mut String,
    ) {
        self.argument(argument, buffer);
        buffer.push(' ');

        let f = self.not_indented();
        match comment {
            CommentedArgumentComment::BracketComment(comment) => {
                f.bracket_comment(comment, buffer);
            }
            CommentedArgumentComment::LineComment(comment) => {
                f.line_comment(comment, buffer);
            }
        }
    }

    fn binary_operation(
        &mut self,
        lhs: &RefinedArgumentsAtom,
        operation: &RefinedArgumentsAtom,
        rhs: &RefinedArgumentsAtom,
        buffer: &mut String,
    ) {
        let arguments = [lhs, operation, rhs];
        if self.try_to_format_into_single_line(&[""], &arguments, "", buffer) {
            return;
        }

        let mut indented = self.indented();
        self.arguments_atom(lhs, buffer);
        buffer.push('\n');
        indented.arguments_atom(operation, buffer);
        buffer.push('\n');
        indented.arguments_atom(rhs, buffer);
    }

    fn unary_operation(
        &mut self,
        operation: &RefinedArgumentsAtom,
        operand: &RefinedArgumentsAtom,
        buffer: &mut String,
    ) {
        let arguments = [operation, operand];

        if self.try_to_format_into_single_line(&[""], &arguments, "", buffer) {
            return;
        }

        let formatted_operation = {
            let start = buffer.len();
            self.arguments_atom(operation, buffer);
            let end = buffer.len();
            &buffer[start..end]
        };
        if !operation.has_line_comment() {
            match self.configuration.indent_type {
                IndentType::Spaces(spaces)
                    if formatted_operation.trim().chars().count() < spaces =>
                {
                    buffer.push(' ');
                    buffer.push_str(self.arguments_atom_to_str(operand).trim_start());
                    return;
                }
                _ => (),
            }
        }

        buffer.push('\n');
        self.indented().arguments_atom(operand, buffer);
    }

    fn default_format_values(&mut self, rest: &RefinedArgumentsNode, buffer: &mut String) {
        let mut add_newline = false;
        for x in rest {
            if add_newline {
                buffer.push('\n');
            }

            self.arguments_atom(x, buffer);
            add_newline = true;
        }
    }

    fn format_command_line(&mut self, mut rest: RefinedArgumentsNode) -> String {
        let tail = rest.split_off(1);
        let Some(head) = rest.first() else {
            return String::new();
        };
        let mut lines = vec![];
        let mut current_line = self.arguments_atom_to_str(head);
        let mut force_next_line = head.is_commented_argument();

        for arg in tail {
            if let RefinedArgumentsAtom::Atom(ArgumentsAtom::LineComment(arg)) = arg {
                lines.push(current_line);
                current_line = self.line_comment_to_str(&arg);
            } else {
                let mut updated_line = format!("{current_line} ");
                self.not_indented().arguments_atom(&arg, &mut updated_line);
                if force_next_line
                    || (updated_line.chars().count() > self.configuration.line_length)
                    || updated_line.contains('\n')
                    || current_line.trim().starts_with('#')
                {
                    force_next_line = arg.is_commented_argument();
                    lines.push(current_line);
                    current_line = self.arguments_atom_to_str(&arg);
                } else {
                    current_line = updated_line;
                    if arg.is_commented_argument() {
                        force_next_line = true;
                    }
                }
            }
        }

        if !current_line.is_empty() {
            lines.push(current_line);
        }

        lines.join("\n")
    }

    fn format_keyword_with_pairs(&mut self, rest: &RefinedArgumentsNode) -> String {
        let rest = pair_arguments(rest.clone());
        let mut buffer = String::new();
        self.default_format_values(&rest, &mut buffer);
        buffer
    }

    fn format_property(&mut self, args: &RefinedArgumentsNode) -> String {
        let mut result = String::new();
        if self.try_to_format_into_single_line(&[""], args, "", &mut result) {
            return result;
        }

        let mut args = args.clone();
        let rest = args.split_off(1);
        let Some(name) = args.first() else {
            return String::new();
        };

        let mut result = self.arguments_atom_to_str(name);
        result.push('\n');
        self.indented().default_format_values(&rest, &mut result);
        result
    }

    fn format_specialized(
        &mut self,
        first: &RefinedArgumentsAtom,
        rest: &RefinedArgumentsNode,
    ) -> String {
        match &self.active_command {
            Some(CommandSchema {
                canonical_name: Some(name),
                ..
            }) if (name == "set_property") => {
                if let Some(value) = first.get_value() {
                    if value == "PROPERTY" {
                        return self.format_property(rest);
                    }
                }
            }
            _ => (),
        }
        let mut buffer = String::new();
        self.default_format_values(rest, &mut buffer);
        buffer
    }

    fn format_non_option(
        &mut self,
        first: &RefinedArgumentsAtom,
        rest: &RefinedArgumentsNode,
        is_pair: bool,
        is_multi_value_argument: bool,
        buffer: &mut String,
    ) {
        if rest.is_empty() {
            return self.arguments_atom(first, buffer);
        }

        let arguments: Vec<&RefinedArgumentsAtom> = {
            let mut result = vec![first];
            for arg in rest {
                result.push(arg);
            }
            result
        };

        if self.try_to_format_into_single_line(&[""], &arguments, "", buffer) {
            return;
        }

        let can_be_inlined = (!self.favour_expansion) || ((!is_pair) && (!is_multi_value_argument));
        if can_be_inlined {
            let f = self.select_inlining_strategy();
            if f.try_to_format_into_single_line(&[""], &arguments, "", buffer) {
                return;
            }
        }

        let mut f = if first.is_inline_hint() {
            self.clone()
        } else {
            self.indented()
        };
        let formatted_values = match self.get_formatter(first) {
            None => f.format_specialized(first, rest),
            Some(formatter_kind) => match formatter_kind {
                KeywordFormatter::CommandLine => f.format_command_line(rest.clone()),
                KeywordFormatter::Pairs => f.format_keyword_with_pairs(rest),
            },
        };

        self.arguments_atom(first, buffer);
        if formatted_values.is_empty() {
            return;
        }

        buffer.push('\n');
        buffer.push_str(&formatted_values);
    }

    fn section(
        &mut self,
        header: &RefinedArgumentsAtom,
        rest: &RefinedArgumentsNode,
        buffer: &mut String,
    ) {
        if rest.is_empty() {
            return self.arguments_atom(header, buffer);
        }

        let preprocessor = self.get_preprocessor(header);
        let rest = match preprocessor {
            None => rest.clone(),
            Some(preprocessor) => self.preprocess_keyword_values(rest.clone(), &preprocessor),
        };
        let arguments: Vec<&RefinedArgumentsAtom> = {
            let mut result = vec![header];
            for arg in &rest {
                result.push(arg);
            }
            result
        };

        if self.try_to_format_into_single_line(&[""], &arguments, "", buffer) {
            return;
        }

        self.arguments_atom(header, buffer);
        buffer.push('\n');
        self.indented().default_format_values(&rest, buffer);
    }

    fn get_preprocessor(&self, atom: &RefinedArgumentsAtom) -> Option<KeywordPreprocessor> {
        if let Some(InlineHintKind::KeywordPreprocessor(p)) = atom.get_inline_hint_kind() {
            return Some(p);
        }

        match &self.active_schema {
            Some(schema) => atom
                .get_value()
                .and_then(|key| schema.keyword_preprocessors.get(key).cloned()),
            _ => None,
        }
    }

    fn get_formatter(&self, atom: &RefinedArgumentsAtom) -> Option<KeywordFormatter> {
        if let Some(InlineHintKind::KeywordFormatter(f)) = atom.get_inline_hint_kind() {
            return Some(f);
        }

        match &self.active_schema {
            Some(schema) => atom
                .get_value()
                .and_then(|key| schema.keyword_formatters.get(key).cloned()),
            _ => None,
        }
    }

    fn preprocess_keyword_values<'a>(
        &self,
        nodes: RefinedArgumentsNode<'a>,
        preprocessor: &KeywordPreprocessor,
    ) -> RefinedArgumentsNode<'a> {
        let case_insensitive = matches!(self.configuration.sort_order, SortOrder::CaseInsensitive);

        match preprocessor {
            KeywordPreprocessor::Sort => sort_arguments(nodes, case_insensitive),
            KeywordPreprocessor::Unique => keep_unique_arguments(nodes),
            KeywordPreprocessor::SortAndUnique => {
                sort_and_keep_unique_arguments(nodes, case_insensitive)
            }
        }
    }

    fn positional_arguments(&mut self, arguments: &RefinedArgumentsNode, buffer: &mut String) {
        match &self.active_command {
            Some(CommandSchema {
                canonical_name: Some(name),
                ..
            }) if name == "add_custom_target" => {
                buffer.push_str(&self.format_command_line(arguments.clone()));
            }
            _ => {
                self.default_format_values(arguments, buffer);
            }
        }
    }

    fn arguments_atom_to_str(&mut self, atom: &RefinedArgumentsAtom) -> String {
        let mut buffer = String::new();
        self.arguments_atom(atom, &mut buffer);
        buffer
    }

    fn arguments_atom(&mut self, atom: &RefinedArgumentsAtom, buffer: &mut String) {
        match atom {
            RefinedArgumentsAtom::Atom(atom) => match atom {
                ArgumentsAtom::Argument(argument) => {
                    self.argument(argument, buffer);
                }
                ArgumentsAtom::BracketComment(comment) => {
                    self.bracket_comment(comment, buffer);
                }
                ArgumentsAtom::CommentedArgument { argument, comment } => {
                    self.commented_argument(argument, comment, buffer);
                }
                ArgumentsAtom::LineComment(comment) => {
                    self.line_comment(comment, buffer);
                }
            },
            RefinedArgumentsAtom::BinaryOperation {
                lhs,
                operation,
                rhs,
            } => {
                self.binary_operation(lhs, operation, rhs, buffer);
            }
            RefinedArgumentsAtom::UnaryOperation { operation, operand } => match operand {
                None => {
                    self.arguments_atom(operation, buffer);
                }
                Some(operand) => {
                    self.unary_operation(operation, operand, buffer);
                }
            },
            RefinedArgumentsAtom::PositionalArguments(arguments) => {
                self.positional_arguments(arguments, buffer);
            }
            RefinedArgumentsAtom::OptionArgument { keyword } => {
                self.arguments_atom(keyword, buffer);
            }
            RefinedArgumentsAtom::OneValueArgument {
                keyword: first,
                arguments: rest,
            } => {
                self.format_non_option(first, rest, false, false, buffer);
            }
            RefinedArgumentsAtom::MultiValueArgument {
                keyword: first,
                arguments: rest,
            } => {
                let preprocessor = self.get_preprocessor(first);
                let rest = match preprocessor {
                    None => rest.clone(),
                    Some(preprocessor) => {
                        self.preprocess_keyword_values(rest.clone(), &preprocessor)
                    }
                };
                self.format_non_option(first, &rest, false, true, buffer);
            }
            RefinedArgumentsAtom::Pair { first, rest } => {
                self.format_non_option(first, rest, true, false, buffer);
            }
            RefinedArgumentsAtom::KeywordArgument {
                first,
                in_between,
                second,
            } => {
                let rest = in_between
                    .clone()
                    .into_iter()
                    .map(RefinedArgumentsAtom::Atom)
                    .chain([RefinedArgumentsAtom::Atom(second.clone())])
                    .collect::<RefinedArgumentsNode>();
                self.format_non_option(
                    &RefinedArgumentsAtom::Atom(first.clone()),
                    &rest,
                    false,
                    false,
                    buffer,
                );
            }
            RefinedArgumentsAtom::Section { header, values } => {
                self.section(header, values, buffer);
            }
        }
    }

    fn group_size(group: &RefinedArgumentsAtom) -> usize {
        match group {
            RefinedArgumentsAtom::PositionalArguments(arguments)
            | RefinedArgumentsAtom::OneValueArgument { arguments, .. }
            | RefinedArgumentsAtom::MultiValueArgument { arguments, .. } => arguments.len(),
            RefinedArgumentsAtom::Section { values, .. } => {
                let section_size = values.len();
                let subarguments_size = values.iter().map(Self::group_size).max().unwrap_or(0);
                std::cmp::max(section_size, subarguments_size)
            }
            _ => 0,
        }
    }

    fn inhibit_favour_expansion(&self) -> bool {
        match self.active_command {
            Some(CommandSchema {
                inhibit_favour_expansion,
                ..
            }) => *inhibit_favour_expansion,
            _ => false,
        }
    }

    fn inlining_condition(&self, groups: &RefinedArgumentsNode) -> bool {
        let mut group_sizes = groups.iter().map(Self::group_size);
        let threshold = if (matches!(
            self.configuration.list_expansion,
            ListExpansion::FavourExpansion
        )) && (!self.inhibit_favour_expansion())
        {
            1
        } else {
            4
        };
        group_sizes.all(|x| x <= threshold)
    }

    fn split_inline_hint_argument<'a>(
        &self,
        argument: RefinedArgumentsAtom<'a>,
    ) -> RefinedArgumentsAtom<'a> {
        match argument {
            RefinedArgumentsAtom::MultiValueArgument { keyword, arguments } => {
                let arguments = match keyword.get_inline_hint_kind() {
                    Some(InlineHintKind::AsCommand { command }) => {
                        let f = self.patch_active_command(self.schemas.get(&command));
                        let arguments = f.preprocess_refined_arguments(arguments);
                        let f = f.patch_active_schema(f.get_signature(&arguments));
                        f.split_arguments(arguments)
                    }
                    _ => arguments,
                };
                RefinedArgumentsAtom::MultiValueArgument { keyword, arguments }
            }
            _ => argument,
        }
    }

    fn split_arguments<'a>(&self, arguments: RefinedArgumentsNode<'a>) -> RefinedArgumentsNode<'a> {
        match &self.active_schema {
            Some(schema) => schema.split_arguments_with_sections(arguments),
            _ => arguments,
        }
        .into_iter()
        .map(|arg| self.split_inline_hint_argument(arg))
        .collect()
    }

    fn arguments(&mut self, arguments: &RefinedArgumentsNode, buffer: &mut String) {
        let mut add_newline = false;
        for x in arguments {
            if add_newline {
                buffer.push('\n');
            }
            self.arguments_atom(x, buffer);
            if !add_newline {
                add_newline = true;
            }
        }
    }

    fn format_command_with_short_name(
        &self,
        begin: &[&str],
        arguments: &RefinedArgumentsNode,
        end: &str,
        buffer: &mut String,
    ) {
        let have_no_line_comments = !is_line_comment_in_any_of(arguments);
        buffer.push_str(&self.indent_symbol);
        for part in begin {
            buffer.push_str(part);
        }
        let formatted_arguments_has_newline = {
            let mut inner_buffer = String::new();
            self.indented().arguments(arguments, &mut inner_buffer);
            let inner_result = inner_buffer.trim_start().contains('\n');
            buffer.push_str(inner_buffer.trim_start());
            inner_result
        };

        if have_no_line_comments && (!formatted_arguments_has_newline) {
            buffer.push_str(end);
        } else {
            buffer.push('\n');
            buffer.push_str(&self.indent_symbol);
            buffer.push_str(end);
        }
    }

    fn format_signature(
        &self,
        identifier: &str,
        mut arguments: RefinedArgumentsNode<'_>,
        buffer: &mut String,
    ) {
        let (name, paren) = self.format_command_name(identifier);
        let begin = [&name, paren];
        let end = ")";

        let initial_buffer_end = buffer.len();
        if self.try_to_format_into_single_line(&begin, &arguments, end, buffer) {
            arguments = self.split_arguments(arguments);
            if self.inlining_condition(&arguments) {
                return;
            }
            buffer.truncate(initial_buffer_end);
        } else {
            arguments = self.split_arguments(arguments);
        }

        let f = self.select_expansion_strategy();
        match f.configuration.indent_type {
            IndentType::Spaces(spaces)
                if begin.iter().map(|part| part.chars().count()).sum::<usize>() == spaces =>
            {
                f.format_command_with_short_name(&begin, &arguments, end, buffer);
            }
            _ => {
                buffer.push_str(&f.indent_symbol);
                for part in begin {
                    buffer.push_str(part);
                }
                buffer.push('\n');
                f.indented().arguments(&arguments, buffer);
                buffer.push('\n');
                buffer.push_str(&f.indent_symbol);
                buffer.push_str(end);
            }
        }
    }

    fn patch_active_schema<'a>(&'a self, schema: Option<&'a ArgumentSchema>) -> FormatterImpl<'a> {
        let mut result = self.clone();
        if let Some(schema) = schema {
            result.active_schema = Some(schema);
        }
        result
    }

    fn format_command(&self, identifier: &str, arguments: ArgumentsNode, buffer: &mut String) {
        let arguments = self.preprocess_arguments(arguments);
        let signature = self.get_signature(&arguments);
        let f = self.patch_active_schema(signature);

        match f.active_command {
            Some(CommandSchema {
                details:
                    CommandSchemaDetails::SpecializedCommand {
                        ref specialization, ..
                    },
                ..
            }) if specialization == "condition_syntax_with_dedent" => f.dedented(),
            _ => f,
        }
        .format_signature(identifier, arguments, buffer);
    }

    fn known_command(&self, identifier: &str, arguments: ArgumentsNode, buffer: &mut String) {
        self.patch_active_command(self.schemas.get(identifier))
            .format_command(identifier, arguments, buffer);
    }

    fn format_command_name<'a>(&'a self, name: &'a str) -> (Cow<'a, str>, &'a str) {
        match &self.active_command {
            Some(CommandSchema {
                canonical_name: Some(value),
                ..
            }) => (value.into(), "("),
            _ => {
                if name.contains('@') {
                    (name.into(), "(")
                } else {
                    (name.to_lowercase().into(), "(")
                }
            }
        }
    }

    fn try_to_format_into_single_line<Part: HasLineComment + TryToFormatIntoSingleLinePart>(
        &self,
        prefixes: &[&str],
        parts: &[Part],
        postfix: &str,
        buffer: &mut String,
    ) -> bool {
        if self.favour_expansion {
            return false;
        }

        if !line_comment_is_only_at_rightmost_edge(parts, postfix) {
            return false;
        }

        let prefix_length = prefixes
            .iter()
            .map(|part| part.chars().count())
            .sum::<usize>();
        let reserved_space =
            prefix_length + postfix.chars().count() + self.indent_symbol.chars().count();
        {
            let initial_buffer_end = buffer.len();

            let mut f = self.not_indented();
            let limit = f.configuration.line_length;

            buffer.push_str(&self.indent_symbol);
            for part in prefixes {
                buffer.push_str(part);
            }
            let mut line_length = reserved_space;

            let mut add_space = false;

            for part in parts {
                let part = {
                    if add_space {
                        buffer.push(' ');
                    }
                    let start = buffer.len();
                    part.format_into_buffer(&mut f, buffer);
                    let end = buffer.len();
                    &buffer[start..end]
                };
                if part.contains('\n') {
                    buffer.truncate(initial_buffer_end);
                    return false;
                }

                line_length += part.chars().count();
                if line_length > limit {
                    buffer.truncate(initial_buffer_end);
                    return false;
                }

                line_length += 1;
                add_space = true;
            }
            buffer.push_str(postfix);
            true
        }
    }

    fn custom_command(
        &self,
        indentation: &str,
        name: &str,
        formatted_node: &str,
        position: &Position,
        buffer: &mut String,
    ) {
        let (command_name, paren) = self.format_command_name(name);
        let begin = &[&self.indent_symbol, &command_name, paren];
        self.unknown_commands_used.borrow_mut().push((
            name.to_string(),
            position.line,
            position.column,
        ));

        if formatted_node.is_empty() {
            for part in begin {
                buffer.push_str(part);
            }
            buffer.push(')');
            return;
        }

        if self.not_indented().try_to_format_into_single_line(
            begin,
            &[&formatted_node],
            ")",
            buffer,
        ) {
            return;
        }

        let indent_symbol = remove_common_beginning(&self.indent_symbol, indentation);
        let content = preprocess_content(formatted_node);
        let body = safe_indent(&content, &indent_symbol);
        let body: &str = if formatted_node.starts_with('\n') {
            &body
        } else {
            body.trim_start_matches(indent_symbol.as_str())
        };

        for part in begin {
            buffer.push_str(part);
        }
        buffer.push_str(body);

        if !body.contains('\n') {
        } else if body.ends_with('\n') {
            buffer.push_str(&self.indent_symbol);
        } else {
            buffer.push('\n');
            buffer.push_str(&self.indent_symbol);
        }
        buffer.push(')');
    }

    fn command_invocation(&self, node: CommandInvocation, buffer: &mut String) {
        match node {
            CommandInvocation::KnownCommand {
                ref identifier,
                arguments,
            } => {
                self.known_command(identifier, arguments, buffer);
            }
            CommandInvocation::CustomCommand {
                ref indentation,
                ref identifier,
                formatted_node,
                ref position,
                ..
            } => self.custom_command(indentation, identifier, formatted_node, position, buffer),
        }
    }

    fn command(&self, node: Command, buffer: &mut String) {
        match node {
            Command::Element {
                command_invocation,
                line_comment,
            } => {
                self.command_invocation(command_invocation, buffer);

                match line_comment {
                    None => (),
                    Some(line_comment) => {
                        buffer.push(' ');
                        self.not_indented().line_comment(&line_comment, buffer);
                    }
                }
            }
            Command::Invocation(node) => {
                self.command_invocation(node, buffer);
            }
        }
    }

    fn bracket_comment(&self, node: &BracketComment, buffer: &mut String) {
        buffer.push_str(&self.indent_symbol);
        buffer.push('#');
        buffer.push_str(node.value);
    }

    fn line_comment_to_str(&self, node: &LineComment) -> String {
        let mut buffer = String::new();
        self.line_comment(node, &mut buffer);
        buffer
    }

    fn line_comment(&self, node: &LineComment, buffer: &mut String) {
        buffer.push_str(&self.indent_symbol);
        buffer.push('#');
        buffer.push_str(node.value.trim_end());
    }

    fn file_element(&self, node: FileElement, buffer: &mut String) {
        match node {
            FileElement::Block { start, body, end } => {
                self.command(start, buffer);
                buffer.push('\n');
                self.block_body(body, buffer);
                self.command(end, buffer);
            }
            FileElement::Command(node) => {
                self.command(node, buffer);
            }
            FileElement::StandaloneIdentifier { value } => {
                buffer.push_str(&self.indent_symbol);
                buffer.push_str(value);
            }
            FileElement::NonCommandElement {
                bracket_comments,
                line_comment,
            } => {
                let mut first = true;
                for x in &bracket_comments {
                    if first {
                        first = false;
                    } else {
                        buffer.push(' ');
                    }
                    self.bracket_comment(x, buffer);
                }
                match line_comment {
                    None => (),
                    Some(line_comment) => {
                        if !bracket_comments.is_empty() {
                            buffer.push(' ');
                        }
                        self.line_comment(&line_comment, buffer);
                    }
                }
            }
            FileElement::NewlineOrGap { value } => {
                buffer.push_str(value);
            }
        }
    }

    fn start(&self, node: Start, size_hint: usize) -> String {
        let mut result = String::with_capacity(size_hint * 6 / 5);
        for child in node.children {
            self.file_element(child, &mut result);
        }

        if !result.ends_with('\n') {
            result.push('\n');
        }
        result
    }
}

fn format(
    node: Start,
    size_hint: usize,
    configuration: &OutcomeConfiguration,
    schemas: &CommandSchemas,
) -> (String, UnknownCommandsUsed) {
    let unknown_commands_used: RefCell<UnknownCommandsUsed> = UnknownCommandsUsed::new().into();
    let formatter = FormatterImpl {
        active_schema: None,
        active_command: None,
        favour_expansion: false,
        indent_symbol: Cow::from(""),

        unknown_commands_used: &unknown_commands_used,
        configuration,
        schemas,
    };
    let formatted_code = formatter.start(node, size_hint);
    (formatted_code, unknown_commands_used.into_inner())
}

#[pyclass]
pub struct Formatter {
    configuration: OutcomeConfiguration,
    schemas: CommandSchemas,
    lines_to_format: Vec<LineRange>,
}

const GERSEMI_OFF: &str = "# gersemi: off";
const GERSEMI_ON: &str = "# gersemi: on";
const CMAKE_FORMAT_OFF: &str = "# cmake-format: off";
const CMAKE_FORMAT_ON: &str = "# cmake-format: on";
const FMT_OFF: &str = "# fmt: off";
const FMT_ON: &str = "# fmt: on";

const BUG: &str =
    "#-#-# gersemi: If you see this there is a bug in gersemi, please report it.#-#-#";

fn line_range_fence_off() -> &'static str {
    static VALUE: LazyLock<String> = LazyLock::new(|| format!("{GERSEMI_OFF}\n{BUG}\n"));
    VALUE.as_str()
}

fn line_range_fence_on() -> &'static str {
    static VALUE: LazyLock<String> = LazyLock::new(|| format!("{BUG}\n{GERSEMI_ON}\n"));
    VALUE.as_str()
}

fn add_line_range_fences(code: String, lines_to_format: &[LineRange]) -> String {
    if lines_to_format.is_empty() {
        return code;
    }

    let lines: Vec<_> = code.split_inclusive('\n').collect();

    let number_of_lines = lines.len();
    let ends: Vec<_> = lines_to_format.iter().map(|x| x.end).collect();
    if ends.iter().max().copied().unwrap_or(0) > number_of_lines {
        return code;
    }

    let starts: Vec<_> = lines_to_format.iter().map(|x| x.start).collect();

    let mut result = Vec::<&str>::new();
    if !starts.contains(&1) {
        result.push(line_range_fence_off());
    }

    for (line_number, line) in (1..).zip(lines) {
        if starts.contains(&line_number) && (line_number != 1) {
            result.push(line_range_fence_on());
        }

        result.push(line);

        if ends.contains(&line_number) && (line_number != number_of_lines) {
            result.push(line_range_fence_off());
        }
    }

    if !ends.contains(&number_of_lines) {
        result.push(line_range_fence_on());
    }

    result.into_iter().collect::<String>()
}

fn disabled_formatting_fences() -> &'static HashMap<&'static str, &'static str> {
    static VALUE: LazyLock<HashMap<&str, &str>> = LazyLock::new(|| {
        let mut value = HashMap::new();
        value.insert(GERSEMI_OFF, GERSEMI_ON);
        value.insert(CMAKE_FORMAT_OFF, CMAKE_FORMAT_ON);
        value.insert(FMT_OFF, FMT_ON);
        value
    });
    &VALUE
}

fn consume_until<'a>(iterator: &mut SplitInclusive<'a, char>, target: &str) -> Option<&'a str> {
    loop {
        match iterator.next() {
            None => {
                return None;
            }
            Some(line) => {
                if line.trim() == target {
                    return Some(line);
                }
            }
        }
    }
}

fn reconstruct_disabled_formatting_zones(original: &str, formatted: String) -> String {
    if disabled_formatting_fences()
        .keys()
        .all(|x| !original.contains(x))
    {
        return formatted;
    }

    let mut other = original.split_inclusive('\n');
    let mut active = formatted.split_inclusive('\n');
    let mut closing_fence: Option<&str> = None;
    let mut line: &str;

    let mut result = Vec::<&str>::new();
    while let Some(next_line) = active.next() {
        line = next_line;
        let command = line.trim();

        if closing_fence.is_none() {
            closing_fence = disabled_formatting_fences().get(command).map(|v| &**v);
            if closing_fence.is_some() {
                consume_until(&mut other, command);
                (other, active) = (active, other);
            }
        }

        if Some(command) == closing_fence {
            let gersemi_on = consume_until(&mut other, command);
            if let Some(gersemi_on) = gersemi_on {
                line = gersemi_on;
            }

            (other, active) = (active, other);
            closing_fence = None;
        }

        result.push(line);
    }

    result.into_iter().collect::<String>()
}

fn line_range_fence_regex() -> Regex {
    let off_pattern = format!("[ \t]*{GERSEMI_OFF}\\n{BUG}\\n");
    let on_pattern = format!("{BUG}\\n[ \t]*{GERSEMI_ON}\\n");
    let pattern = format!("{off_pattern}|{on_pattern}");
    Regex::new(&pattern).unwrap()
}

fn remove_line_range_fences(formatted_code: &str) -> String {
    static PATTERN: LazyLock<Regex> = LazyLock::new(line_range_fence_regex);
    PATTERN.replace_all(formatted_code, "").to_string()
}

fn get_keyword_transformers(
    hints: Vec<String>,
) -> (
    HashMap<String, KeywordFormatter>,
    HashMap<String, KeywordPreprocessor>,
) {
    let mut formatters = HashMap::<String, KeywordFormatter>::new();
    let mut preprocessors = HashMap::<String, KeywordPreprocessor>::new();

    let yaml = Yaml::new();
    for hint in hints {
        let Ok(Value::Mapping(m)) = yaml.load_str(&hint) else {
            continue;
        };

        for (keyword, hint) in m {
            let (Value::String(keyword), Value::String(hint)) = (keyword, hint) else {
                continue;
            };

            if let Some(hint) = KeywordFormatter::from_str(&hint) {
                formatters.insert(keyword, hint);
            } else if let Some(hint) = KeywordPreprocessor::from_str(&hint) {
                preprocessors.insert(keyword, hint);
            }
        }
    }

    (formatters, preprocessors)
}

fn create_standard_command_schema(
    positional_arguments: Vec<String>,
    keywords: Keywords,
) -> ArgumentSchema {
    let (keyword_formatters, keyword_preprocessors) = get_keyword_transformers(keywords.hints);

    ArgumentSchema {
        options: single_word_matchers(keywords.options),
        one_value_keywords: single_word_matchers(keywords.one_value_keywords),
        multi_value_keywords: single_word_matchers(keywords.multi_value_keywords),
        front_positional_arguments: positional_arguments,
        back_positional_arguments: Vec::new(),
        sections: HashMap::new(),
        keyword_preprocessors,
        keyword_formatters,
    }
}

fn create_command_schema(content: CustomCommandContent) -> CommandSchema {
    CommandSchema {
        block_end: content.block_end,
        canonical_name: Some(content.canonical_name),
        inhibit_favour_expansion: false,
        details: CommandSchemaDetails::StandardCommand {
            schema: create_standard_command_schema(content.positional_arguments, content.keywords),
            signatures: Signatures::new(),
            two_words_keywords: Vec::new(),
        },
    }
}

fn get_just_schemas(definitions: Vec<(String, Vec<CustomCommand>)>) -> CommandSchemaMapping {
    let mut result = CommandSchemaMapping::new();
    for (name, mut info) in definitions {
        info.sort_by(|a, b| a.1.cmp(&b.1));
        if let Some((content, _)) = info.into_iter().next() {
            result.insert(name, create_command_schema(content));
        }
    }
    result
}

#[pymethods]
impl Formatter {
    #[new]
    pub fn new(py: Python, configuration: Configuration) -> PyResult<Self> {
        let definitions = find_all_custom_command_definitions(py, &configuration)?;
        let definition_schemas = get_just_schemas(definitions);
        let extension_schemas =
            load_definitions_from_extensions(&configuration.outcome.extensions)?;
        Ok(Self {
            configuration: configuration.outcome,
            schemas: CommandSchemas::new(definition_schemas, extension_schemas),
            lines_to_format: configuration.control.line_ranges,
        })
    }

    pub fn format(&self, text: String) -> Result<(String, UnknownCommandsUsed), PyErr> {
        let text = add_line_range_fences(text, &self.lines_to_format);
        let parser = Parser::new(&text, &self.schemas);
        let node = parser.start()?;
        let before = if self.configuration.disable_sanity_checks {
            None
        } else {
            Some(node.clone())
        };

        let size_hint = text.len();
        let (result, warnings) = format(node, size_hint, &self.configuration, &self.schemas);
        if let Some(before) = before {
            let parser = Parser::new(&result, &self.schemas);
            let after = parser.start()?;
            if !check_equivalence(before, after) {
                return Err(PyRuntimeError::new_err(
                    "Reformatting doesn't produce equivalent code.",
                ));
            }
        }

        let result = reconstruct_disabled_formatting_zones(&text, result);
        let result = if self.lines_to_format.is_empty() {
            result
        } else {
            remove_line_range_fences(&result)
        };
        Ok((result, warnings))
    }
}
