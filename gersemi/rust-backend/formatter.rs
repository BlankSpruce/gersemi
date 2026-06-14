use crate::argument_schema::{
    ArgumentSchema, CommandSchema, CommandSchemaDetails, CommandSchemas, KeywordMatcher, Signatures,
};
use crate::configuration::{
    IndentType, KeywordFormatter, KeywordPreprocessor, ListExpansion, OutcomeConfiguration,
    SortOrder,
};
use crate::keyword_preprocessor::{
    keep_unique_arguments, sort_and_keep_unique_arguments, sort_arguments,
};
use crate::node::{
    Argument, ArgumentsAtom, ArgumentsNode, BracketComment, Command, CommandInvocation,
    CommentedArgumentComment, FileElement, LineComment, Position, RefinedArgumentsAtom,
    RefinedArgumentsNode, Start,
};
use crate::parser::{quoted_argument_pattern, regex};
use crate::two_words_keyword_isolator::TwoWordKeywordMatcher;
use std::cell::RefCell;
use std::iter::zip;

pub type UnknownCommandsUsed = Vec<(String, usize, usize)>;

#[derive(Clone)]
struct Formatter<'a> {
    active_command: Option<CommandSchema>,
    favour_expansion: bool,
    indent_symbol: String,

    unknown_commands_used: &'a RefCell<UnknownCommandsUsed>,

    configuration: &'a OutcomeConfiguration,
    schemas: &'a CommandSchemas,
}

pub fn remove_common_beginning(s: &str, other: &str) -> String {
    let mut index = 0;
    for (lhs, rhs) in zip(s.chars(), other.chars()) {
        if lhs != rhs {
            break;
        }
        index += 1;
    }

    s[index..].to_string()
}

pub fn strip_empty_lines_from_edges(s: &str) -> String {
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

pub fn ends_with_line_comment(s: &str) -> bool {
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
    let re = regex(pattern);
    match re.find(s) {
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
    let regex_start = regex(r"\[(=*)\[");
    if let Some(captures) = regex_start.captures(s) {
        if let Some(matched_left_bracket) = captures.get(1) {
            let equal_signs = "=".repeat(matched_left_bracket.len());
            let pattern = format!(r"\[{equal_signs}\[([\s\S]+?)\]{equal_signs}\]");
            return flat_split(&pattern, s);
        }
    }

    (s.to_string(), None)
}

fn split_by_quoted_arguments(s: &String) -> Vec<String> {
    let re = regex(quoted_argument_pattern());
    let mut s: &str = s;
    let mut result = Vec::<String>::new();
    while let Some(matched) = re.find(s) {
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
    s.split_inclusive('\n')
        .map(|line| {
            if predicate(line) {
                format!("{indent_symbol}{line}")
            } else {
                line.to_string()
            }
        })
        .collect::<String>()
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

pub fn safe_indent(s: &str, indent_symbol: &str) -> String {
    let result = split_into_segments(s)
        .into_iter()
        .map(|x| indent_segment(&x, indent_symbol))
        .collect::<Vec<String>>();
    result.into_iter().collect::<String>()
}

trait HasLineComment {
    fn has_line_comment(&self) -> bool;
}

impl HasLineComment for ArgumentsAtom {
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

impl HasLineComment for RefinedArgumentsAtom {
    fn has_line_comment(&self) -> bool {
        (&self).has_line_comment()
    }
}

impl HasLineComment for &RefinedArgumentsAtom {
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

fn is_line_comment_in_any_of(arguments: &RefinedArgumentsNode) -> bool {
    arguments.iter().any(HasLineComment::has_line_comment)
}

fn pair_arguments(arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
    let mut result = RefinedArgumentsNode::new();
    let mut accumulator = RefinedArgumentsNode::new();
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

impl Formatter<'_> {
    fn not_indented(&self) -> Self {
        let mut result = self.clone();
        result.indent_symbol = String::new();
        result
    }

    fn indented(&self) -> Self {
        let mut result = self.clone();
        result.indent_symbol = format!(
            "{}{}",
            self.configuration.indent_type.as_string(),
            self.indent_symbol
        );
        result
    }

    fn dedented(&self) -> Self {
        let indent_type = self.configuration.indent_type.as_string();
        let mut result = self.clone();
        result.indent_symbol = self
            .indent_symbol
            .strip_prefix(&indent_type)
            .get_or_insert("")
            .to_string();
        result
    }

    fn patched(&self, active_command: Option<CommandSchema>) -> Self {
        if active_command.is_none() {
            return self.clone();
        }
        let mut result = self.clone();
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

    fn block_body(&self, node: Vec<FileElement>) -> String {
        let f = self.indented();
        node.into_iter()
            .map(|x| f.file_element(x))
            .collect::<String>()
    }

    fn get_patch(&self, identifier: &str) -> Option<CommandSchema> {
        let identifier = identifier.to_lowercase();
        self.schemas.get(&identifier).cloned()
    }

    fn two_words_keywords(&self) -> &Vec<TwoWordKeywordMatcher> {
        static EMPTY: Vec<TwoWordKeywordMatcher> = vec![];
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

    fn standard_preprocess_arguments(&self, arguments: ArgumentsNode) -> RefinedArgumentsNode {
        crate::two_words_keyword_isolator::preprocess_arguments(
            self.two_words_keywords(),
            arguments
                .into_iter()
                .map(RefinedArgumentsAtom::Atom)
                .collect(),
        )
    }

    fn preprocess_arguments(&self, arguments: ArgumentsNode) -> RefinedArgumentsNode {
        if self.shall_use_condition_syntax() {
            crate::argument_schema::isolate_conditions(
                arguments
                    .into_iter()
                    .map(RefinedArgumentsAtom::Atom)
                    .collect(),
            )
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
        for (item, signature) in signatures {
            let Some(item) = item else {
                continue;
            };
            if atom.is_one_of_keywords(std::slice::from_ref(item)) {
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

    fn standard_complex_argument(&self, arguments: &ArgumentsNode) -> String {
        if arguments.len() <= 4 {
            if let Some(result) =
                self.try_to_format_into_single_line("(", arguments, ")", |formatter, x| {
                    let x = RefinedArgumentsAtom::Atom(x.clone());
                    formatter.arguments_atom(&x)
                })
            {
                return result;
            }
        }

        let begin = self.indent("(\n");
        let arguments = self.indented().arguments(
            arguments
                .iter()
                .map(|x| RefinedArgumentsAtom::Atom(x.clone()))
                .collect(),
        );
        let end = self.indent(")");
        format!("{begin}{arguments}\n{end}")
    }

    fn condition_syntax_complex_argument(&self, arguments: &ArgumentsNode) -> String {
        let arguments = self.preprocess_arguments(arguments.clone());
        if let Some(result) =
            self.try_to_format_into_single_line("(", &arguments, ")", |formatter, x| {
                formatter.arguments_atom(x)
            })
        {
            return result;
        }

        let begin = self.indent("(\n");
        let formatted_arguments = self.indented().arguments(arguments);
        let end = self.indent(")");
        format!("{begin}{formatted_arguments}\n{end}")
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

    fn complex_argument(&self, arguments: &ArgumentsNode) -> String {
        if self.shall_use_condition_syntax() {
            self.condition_syntax_complex_argument(arguments)
        } else {
            self.standard_complex_argument(arguments)
        }
    }

    fn argument(&self, argument: &Argument) -> String {
        match argument {
            Argument::Bracket {
                start, value, end, ..
            } => format!("{}{start}{value}{end}", self.indent_symbol),
            Argument::Complex { arguments } => self.complex_argument(arguments),
            Argument::Quoted { value, .. } => format!("{}\"{value}\"", self.indent_symbol),
            Argument::Unquoted { value, .. } => format!("{}{value}", self.indent_symbol),
        }
    }

    fn commented_argument(
        &self,
        argument: &Argument,
        comment: &CommentedArgumentComment,
    ) -> String {
        let comment = {
            let f = self.not_indented();
            match comment {
                CommentedArgumentComment::BracketComment(comment) => f.bracket_comment(comment),
                CommentedArgumentComment::LineComment { comment, .. } => f.line_comment(comment),
            }
        };
        format!("{} {comment}", self.argument(argument))
    }

    fn binary_operation(
        &mut self,
        lhs: &RefinedArgumentsAtom,
        operation: &RefinedArgumentsAtom,
        rhs: &RefinedArgumentsAtom,
    ) -> String {
        let arguments = [lhs, operation, rhs];
        if let Some(result) =
            self.try_to_format_into_single_line("", &arguments, "", |formatter, x| {
                formatter.arguments_atom(x)
            })
        {
            return result;
        }

        let mut indented = self.indented();
        format!(
            "{}\n{}\n{}",
            self.arguments_atom(lhs),
            indented.arguments_atom(operation),
            indented.arguments_atom(rhs)
        )
    }

    fn unary_operation(
        &mut self,
        operation: &RefinedArgumentsAtom,
        operand: &RefinedArgumentsAtom,
    ) -> String {
        let arguments = [operation, operand];

        if let Some(result) =
            self.try_to_format_into_single_line("", &arguments, "", |formatter, x| {
                formatter.arguments_atom(x)
            })
        {
            return result;
        }

        let formatted_operation = self.arguments_atom(operation);
        if !operation.has_line_comment() {
            match self.configuration.indent_type {
                IndentType::Spaces(spaces) if formatted_operation.trim().len() < spaces => {
                    return format!(
                        "{formatted_operation} {}",
                        self.arguments_atom(operand).trim_start()
                    );
                }
                _ => (),
            }
        }

        format!(
            "{formatted_operation}\n{}",
            self.indented().arguments_atom(operand)
        )
    }

    fn default_format_values(&mut self, rest: &RefinedArgumentsNode) -> String {
        rest.iter()
            .map(|x| self.arguments_atom(x))
            .collect::<Vec<String>>()
            .join("\n")
    }

    fn format_command_line(&mut self, mut rest: RefinedArgumentsNode) -> String {
        let tail = rest.split_off(1);
        let Some(head) = rest.first() else {
            return String::new();
        };
        let mut lines = vec![];
        let mut current_line = self.arguments_atom(head);
        let mut force_next_line = head.is_commented_argument();

        for arg in tail {
            if let RefinedArgumentsAtom::Atom(ArgumentsAtom::LineComment(arg)) = arg {
                lines.push(current_line);
                current_line = self.line_comment(&arg);
            } else {
                let formatted_arg = self.not_indented().arguments_atom(&arg);
                let updated_line = format!("{current_line} {formatted_arg}");
                if force_next_line
                    || (updated_line.len() > self.configuration.line_length)
                    || updated_line.contains('\n')
                    || current_line.trim().starts_with('#')
                {
                    force_next_line = arg.is_commented_argument();
                    lines.push(current_line);
                    current_line = self.arguments_atom(&arg);
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
        self.default_format_values(&rest)
    }

    fn format_property(&mut self, args: &RefinedArgumentsNode) -> String {
        if let Some(result) = self.try_to_format_into_single_line("", args, "", |formatter, x| {
            formatter.arguments_atom(x)
        }) {
            return result;
        }

        let mut args = args.clone();
        let rest = args.split_off(1);
        let Some(name) = args.first() else {
            return String::new();
        };

        format!(
            "{}\n{}",
            self.arguments_atom(name),
            self.indented().default_format_values(&rest)
        )
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
        self.default_format_values(rest)
    }

    fn format_non_option(
        &mut self,
        first: &RefinedArgumentsAtom,
        rest: &RefinedArgumentsNode,
        is_pair: bool,
        is_multi_value_argument: bool,
    ) -> String {
        if rest.is_empty() {
            return self.arguments_atom(first);
        }

        let arguments: Vec<&RefinedArgumentsAtom> = {
            let mut result = vec![first];
            for arg in rest {
                result.push(arg);
            }
            result
        };

        if let Some(result) =
            self.try_to_format_into_single_line("", &arguments, "", |formatter, x| {
                formatter.arguments_atom(x)
            })
        {
            return result;
        }

        let can_be_inlined = (!self.favour_expansion) || ((!is_pair) && (!is_multi_value_argument));
        if can_be_inlined {
            let f = self.select_inlining_strategy();
            if let Some(result) =
                f.try_to_format_into_single_line("", &arguments, "", |formatter, x| {
                    formatter.arguments_atom(x)
                })
            {
                return result;
            }
        }

        let mut indented = self.indented();
        let formatted_values = match self.get_formatter(first) {
            None => indented.format_specialized(first, rest),
            Some(formatter_kind) => match formatter_kind {
                KeywordFormatter::CommandLine => indented.format_command_line(rest.clone()),
                KeywordFormatter::Pairs => indented.format_keyword_with_pairs(rest),
            },
        };

        if formatted_values.is_empty() {
            return self.arguments_atom(first);
        }

        format!("{}\n{formatted_values}", self.arguments_atom(first))
    }

    fn section(&mut self, header: &RefinedArgumentsAtom, rest: &RefinedArgumentsNode) -> String {
        if rest.is_empty() {
            return self.arguments_atom(header);
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

        if let Some(result) =
            self.try_to_format_into_single_line("", &arguments, "", |formatter, x| {
                formatter.arguments_atom(x)
            })
        {
            return result;
        }

        format!(
            "{}\n{}",
            self.arguments_atom(header),
            self.indented().default_format_values(&rest)
        )
    }

    fn get_preprocessor(&self, atom: &RefinedArgumentsAtom) -> Option<KeywordPreprocessor> {
        match &self.active_command {
            Some(CommandSchema {
                details: CommandSchemaDetails::StandardCommand { schema, .. },
                ..
            }) => atom
                .get_value()
                .and_then(|key| schema.keyword_preprocessors.get(&key).cloned()),
            _ => None,
        }
    }

    fn get_formatter(&self, atom: &RefinedArgumentsAtom) -> Option<KeywordFormatter> {
        match &self.active_command {
            Some(CommandSchema {
                details: CommandSchemaDetails::StandardCommand { schema, .. },
                ..
            }) => atom
                .get_value()
                .and_then(|key| schema.keyword_formatters.get(&key).cloned()),
            _ => None,
        }
    }

    fn preprocess_keyword_values(
        &self,
        nodes: RefinedArgumentsNode,
        preprocessor: &KeywordPreprocessor,
    ) -> RefinedArgumentsNode {
        let case_insensitive = matches!(self.configuration.sort_order, SortOrder::CaseInsensitive);

        match preprocessor {
            KeywordPreprocessor::Sort => sort_arguments(nodes, case_insensitive),
            KeywordPreprocessor::Unique => keep_unique_arguments(nodes),
            KeywordPreprocessor::SortAndUnique => {
                sort_and_keep_unique_arguments(nodes, case_insensitive)
            }
        }
    }

    fn positional_arguments(&mut self, arguments: &RefinedArgumentsNode) -> String {
        match &self.active_command {
            Some(CommandSchema {
                canonical_name: Some(name),
                ..
            }) if name == "add_custom_target" => self.format_command_line(arguments.clone()),
            _ => self.default_format_values(arguments),
        }
    }

    fn arguments_atom(&mut self, atom: &RefinedArgumentsAtom) -> String {
        match atom {
            RefinedArgumentsAtom::Atom(atom) => match atom {
                ArgumentsAtom::Argument(argument) => self.argument(argument),
                ArgumentsAtom::BracketComment(comment) => self.bracket_comment(comment),
                ArgumentsAtom::CommentedArgument { argument, comment } => {
                    self.commented_argument(argument, comment)
                }
                ArgumentsAtom::LineComment(comment) => self.line_comment(comment),
            },
            RefinedArgumentsAtom::BinaryOperation {
                lhs,
                operation,
                rhs,
            } => self.binary_operation(lhs, operation, rhs),
            RefinedArgumentsAtom::UnaryOperation { operation, operand } => match operand {
                None => self.arguments_atom(operation),
                Some(operand) => self.unary_operation(operation, operand),
            },
            RefinedArgumentsAtom::PositionalArguments(arguments) => {
                self.positional_arguments(arguments)
            }
            RefinedArgumentsAtom::OptionArgument { keyword } => self.arguments_atom(keyword),
            RefinedArgumentsAtom::OneValueArgument {
                keyword: first,
                arguments: rest,
            } => self.format_non_option(first, rest, false, false),
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
                self.format_non_option(first, &rest, false, true)
            }
            RefinedArgumentsAtom::Pair { first, rest } => {
                self.format_non_option(first, rest, true, false)
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
                )
            }
            RefinedArgumentsAtom::Section { header, values } => self.section(header, values),
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
            }) => inhibit_favour_expansion,
            _ => false,
        }
    }

    fn inlining_condition(&self, arguments: &RefinedArgumentsNode) -> bool {
        let groups = self.split_arguments(arguments.clone());
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

    fn split_arguments(&self, arguments: RefinedArgumentsNode) -> RefinedArgumentsNode {
        match &self.active_command {
            Some(CommandSchema {
                details: CommandSchemaDetails::StandardCommand { schema, .. },
                ..
            }) => schema.split_arguments_with_sections(arguments),
            _ => arguments,
        }
    }

    fn arguments(&mut self, arguments: RefinedArgumentsNode) -> String {
        let arguments = self.split_arguments(arguments);
        arguments
            .iter()
            .map(|x| self.arguments_atom(x))
            .collect::<Vec<String>>()
            .join("\n")
    }

    fn format_command_with_short_name(
        &self,
        begin: &str,
        arguments: RefinedArgumentsNode,
        end: &str,
    ) -> String {
        let have_no_line_comments = !is_line_comment_in_any_of(&arguments);
        let formatted_arguments = self
            .indented()
            .arguments(arguments)
            .trim_start()
            .to_string();

        if have_no_line_comments && (!formatted_arguments.contains('\n')) {
            return format!("{}{formatted_arguments}{}", self.indent(begin), end);
        }

        format!(
            "{}{formatted_arguments}\n{}",
            self.indent(begin),
            self.indent(end)
        )
    }

    fn format_signature(&self, identifier: &str, arguments: RefinedArgumentsNode) -> String {
        let begin = format!("{}(", self.format_command_name(identifier));
        let end = ")";

        if let Some(result) =
            self.try_to_format_into_single_line(&begin, &arguments, end, |formatter, x| {
                formatter.arguments_atom(x)
            })
        {
            if self.inlining_condition(&arguments) {
                return result;
            }
        }

        let f = self.select_expansion_strategy();
        match f.configuration.indent_type {
            IndentType::Spaces(spaces) if begin.len() == spaces => {
                f.format_command_with_short_name(&begin, arguments, end)
            }
            _ => format!(
                "{}\n{}\n{}",
                f.indent(&begin),
                f.indented().arguments(arguments),
                f.indent(end)
            ),
        }
    }

    fn create_schema_patch(&self, schema: Option<&ArgumentSchema>) -> Option<CommandSchema> {
        let schema = schema?;
        match &self.active_command {
            Some(command_schema) => match &command_schema.details {
                CommandSchemaDetails::StandardCommand {
                    signatures,
                    two_words_keywords,
                    ..
                } => {
                    let mut result = command_schema.clone();
                    result.details = CommandSchemaDetails::StandardCommand {
                        schema: schema.clone(),
                        signatures: signatures.clone(),
                        two_words_keywords: two_words_keywords.clone(),
                    };
                    Some(result)
                }
                CommandSchemaDetails::SpecializedCommand { .. } => None,
            },
            _ => None,
        }
    }

    fn format_command(&self, identifier: &str, arguments: ArgumentsNode) -> String {
        let arguments = self.preprocess_arguments(arguments);
        let signature = self.get_signature(&arguments);
        let signature = self.create_schema_patch(signature);
        let f = self.patched(signature);

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
        .format_signature(identifier, arguments)
    }

    fn known_command(&self, identifier: &str, arguments: ArgumentsNode) -> String {
        self.patched(self.get_patch(identifier))
            .format_command(identifier, arguments)
    }

    fn format_command_name(&self, name: &str) -> String {
        match &self.active_command {
            Some(CommandSchema {
                canonical_name: Some(value),
                ..
            }) => value.clone(),
            _ => {
                if name.contains('@') {
                    name.to_string()
                } else {
                    name.to_lowercase()
                }
            }
        }
    }

    fn indent(&self, value: &str) -> String {
        indent(value, &self.indent_symbol, |x| !x.trim().is_empty())
    }

    fn try_to_format_into_single_line<
        Part: HasLineComment,
        Visitor: Fn(&mut Formatter, &Part) -> String,
    >(
        &self,
        prefix: &str,
        parts: &[Part],
        postfix: &str,
        visitor: Visitor,
    ) -> Option<String> {
        if self.favour_expansion {
            return None;
        }

        if !line_comment_is_only_at_rightmost_edge(parts, postfix) {
            return None;
        }

        let reserved_space = prefix.len() + postfix.len() + self.indent_symbol.len();
        let result = {
            let mut f = self.not_indented();
            let mut result = Vec::<String>::new();
            let mut line_length = reserved_space;

            let limit = f.configuration.line_length;
            for part in parts.iter().map(|p| (visitor)(&mut f, p)) {
                if part.contains('\n') {
                    return None;
                }

                line_length += part.len();
                if line_length > limit {
                    return None;
                }

                result.push(part);
                line_length += 1;
            }
            result.join(" ")
        };

        Some(format!("{}{prefix}{result}{postfix}", self.indent_symbol))
    }

    fn custom_command(
        &self,
        indentation: &str,
        name: String,
        formatted_node: &str,
        position: &Position,
    ) -> String {
        let begin = {
            let s = format!("{}(", self.format_command_name(&name));
            self.indent(&s)
        };
        self.unknown_commands_used
            .borrow_mut()
            .push((name, position.line, position.column));

        if formatted_node.is_empty() {
            return format!("{begin})");
        }

        let result = self.not_indented().try_to_format_into_single_line(
            &begin,
            &[&formatted_node],
            ")",
            |_, x| (*x).to_string(),
        );
        if let Some(result) = result {
            return result;
        }

        let indent_symbol = remove_common_beginning(&self.indent_symbol, indentation);
        let content = preprocess_content(formatted_node);
        let body = safe_indent(&content, &indent_symbol);
        let body: &str = if formatted_node.starts_with('\n') {
            &body
        } else {
            body.trim_start_matches(indent_symbol.as_str())
        };

        let end = if !body.contains('\n') {
            ")".to_string()
        } else if body.ends_with('\n') {
            self.indent(")")
        } else {
            format!("\n{}", self.indent(")"))
        };

        format!("{begin}{body}{end}")
    }

    fn command_invocation(&self, node: CommandInvocation) -> String {
        match node {
            CommandInvocation::KnownCommand {
                ref identifier,
                arguments,
            } => self.known_command(identifier, arguments),
            CommandInvocation::CustomCommand {
                ref indentation,
                identifier,
                ref formatted_node,
                ref position,
                ..
            } => self.custom_command(indentation, identifier, formatted_node, position),
        }
    }

    fn command(&self, node: Command) -> String {
        match node {
            Command::Element {
                command_invocation,
                line_comment,
            } => match line_comment {
                None => self.command_invocation(command_invocation),
                Some(line_comment) => format!(
                    "{} {}",
                    self.command_invocation(command_invocation),
                    self.not_indented().line_comment(&line_comment)
                ),
            },
            Command::Invocation(node) => self.command_invocation(node),
        }
    }

    fn standalone_identifier(&self, value: &str) -> String {
        format!("{}{value}", self.indent_symbol)
    }

    fn bracket_comment(&self, node: &BracketComment) -> String {
        format!("{}#{}", self.indent_symbol, node.value)
    }

    fn line_comment(&self, node: &LineComment) -> String {
        format!("{}#{}", self.indent_symbol, node.value.trim_end())
    }

    fn file_element(&self, node: FileElement) -> String {
        match node {
            FileElement::Block { start, body, end } => {
                let formatted = [
                    self.command(start),
                    self.block_body(body),
                    self.command(end),
                ];
                formatted
                    .into_iter()
                    .filter(|x| !x.is_empty())
                    .collect::<Vec<_>>()
                    .join("\n")
            }
            FileElement::Command(node) => self.command(node),
            FileElement::StandaloneIdentifier { value } => self.standalone_identifier(&value),
            FileElement::NonCommandElement {
                bracket_comments,
                line_comment,
            } => {
                let mut result = bracket_comments
                    .into_iter()
                    .map(|x| self.bracket_comment(&x))
                    .collect::<Vec<_>>()
                    .join(" ");
                match line_comment {
                    None => (),
                    Some(line_comment) => {
                        if !result.is_empty() {
                            result.push(' ');
                        }
                        result.push_str(&self.line_comment(&line_comment));
                    }
                }
                result
            }
            FileElement::NewlineOrGap { value } => value,
        }
    }

    fn start(&self, node: Start) -> String {
        let mut result = node
            .children
            .into_iter()
            .map(|x| self.file_element(x))
            .collect::<String>();
        if !result.ends_with('\n') {
            result.push('\n');
        }
        result
    }
}

pub fn format(
    node: Start,
    configuration: &OutcomeConfiguration,
    schemas: &CommandSchemas,
) -> (String, UnknownCommandsUsed) {
    let unknown_commands_used: RefCell<UnknownCommandsUsed> = UnknownCommandsUsed::new().into();
    let formatter = Formatter {
        active_command: None,
        favour_expansion: false,
        indent_symbol: String::new(),

        unknown_commands_used: &unknown_commands_used,
        configuration,
        schemas,
    };
    let formatted_code = formatter.start(node);
    (formatted_code, unknown_commands_used.into_inner())
}
