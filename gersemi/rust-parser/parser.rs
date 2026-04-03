use pyo3::prelude::*;

#[pymodule]
mod gersemi_rust_parser {
    use pyo3::prelude::*;
    use regex::*;
    use std::sync::LazyLock;

    struct BlockCommand {
        name: String,
        re: regex::Regex,
    }

    struct Parser {
        blocks: Vec<(BlockCommand, BlockCommand)>,
        known_commands: Vec<String>,
        text: String,
    }

    #[pyclass]
    #[derive(Clone)]
    enum Node {
        Tree { data: String, children: Vec<Node> },
        Token { type_: String, value: String },
    }

    #[pyclass(eq, eq_int)]
    #[derive(Clone, PartialEq)]
    enum ErrorType {
        GenericParsingError,
        ParsingError,
        UnbalancedBlock,
        UnbalancedBrackets,
        UnbalancedParentheses,
    }

    #[pyclass]
    #[derive(Clone)]
    struct Error {
        error_type: ErrorType,
        explanation: String,
        line: usize,
        column: usize,
    }

    #[pyclass]
    #[derive(Clone)]
    enum ParsingResult {
        Success(Node),
        Fail {
            error_type: ErrorType,
            explanation: String,
            line: usize,
            column: usize,
        },
    }

    fn tree(data: &str, children: Vec<Node>) -> Node {
        Node::Tree {
            data: data.to_string(),
            children,
        }
    }

    fn token(type_: &str, value: &str) -> Node {
        Node::Token {
            type_: type_.to_string(),
            value: value.to_string(),
        }
    }

    fn add_ignores(pattern: String) -> String {
        format!("^({})[ \t]*", pattern)
    }

    const ESCAPE_SEQUENCE_R: &str = r#"\\([^A-Za-z0-9]|[nrt])"#;
    const IDENTIFIER_R: &str = r"^([A-Za-z_@][A-Za-z0-9_@]*)[ \t]*";
    const MAKE_STYLE_REFERENCE_R: &str = r##"\$\([^\)\n\"#]+?\)"##;
    const QUOTED_CONTINUATION_R: &str = r#"\\\n"#;
    const QUOTED_ELEMENT_R: &str = r#"[^\\\"]|\n"#;

    fn quoted_argument_pattern() -> &'static str {
        static RE: LazyLock<String> = LazyLock::new(|| {
            format!(
                r#""({}|{}|{})*?""#,
                QUOTED_ELEMENT_R, ESCAPE_SEQUENCE_R, QUOTED_CONTINUATION_R
            )
        });
        RE.as_str()
    }

    fn unquoted_legacy_pattern() -> String {
        format!(r##"[^\s\(\)#\"\\]+{}"##, quoted_argument_pattern())
    }

    fn unquoted_argument_pattern() -> &'static str {
        static RE: LazyLock<String> = LazyLock::new(|| {
            format!(
                "^(({}|{}|{}|{}|{})+)[ \t]*",
                unquoted_legacy_pattern(),
                MAKE_STYLE_REFERENCE_R,
                ESCAPE_SEQUENCE_R,
                r##"[^\$\s\(\)#\"\\]+"##,
                r##"[^\s\(\)#\"\\]"##
            )
        });
        RE.as_str()
    }

    fn bracket_argument_pattern(number_of_equal_signs: usize) -> String {
        let equal_signs = "=".repeat(number_of_equal_signs);
        format!(r"^(\[{0}\[[\s\S]+?\]{0}\])[ \t]*", equal_signs)
    }

    fn regex(pattern: &str) -> Regex {
        Regex::new(pattern).unwrap()
    }

    type Match = (Node, usize);
    type SkippableMatch = (Option<Node>, usize);

    impl Parser {
        fn line(&self, offset: usize) -> usize {
            self.text[..offset].chars().filter(|&c| c == '\n').count()
        }

        fn column(&self, offset: usize) -> usize {
            let skip = self.text[..offset].rfind('\n').unwrap_or(0);
            offset - skip
        }

        fn error(&self, offset: usize, error_type: ErrorType) -> Error {
            let line = self.line(offset);
            let column = self.column(offset);
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

        fn bracket_argument_token(&self, offset: usize) -> Result<Option<Match>, Error> {
            static RE_START: LazyLock<Regex> = LazyLock::new(|| regex(r"^\[(=*)\["));
            match RE_START.captures(&self.text[offset..]) {
                None => Ok(None),
                Some(captures) => match captures.get(1) {
                    None => Ok(None),
                    Some(matched_left_bracket) => {
                        let re_pattern = bracket_argument_pattern(matched_left_bracket.len());
                        let re = regex(re_pattern.as_str());
                        match re.captures(&self.text[offset..]) {
                            None => Err(self.unbalanced_brackets(offset)),
                            Some(captures) => Ok(captures.get(1).map(|matched| {
                                (
                                    token("BRACKET_ARGUMENT", matched.as_str()),
                                    offset + captures.get_match().len(),
                                )
                            })),
                        }
                    }
                },
            }
        }

        fn terminal(&self, re: &regex::Regex, name: &str, offset: usize) -> Option<Match> {
            match re.captures(&self.text[offset..]) {
                None => None,
                Some(captures) => captures.get(1).map(|matched| {
                    (
                        token(name, matched.as_str()),
                        offset + captures.get_match().len(),
                    )
                }),
            }
        }

        fn pound_sign(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^(#)"));
            self.terminal(&RE, "POUND_SIGN", offset)
        }

        fn left_paren(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^(\()[ \t]*"));
            self.terminal(&RE, "LEFT_PAREN", offset)
        }

        fn right_paren(&self, offset: usize) -> Result<Match, Error> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^(\))[ \t]*"));
            match self.terminal(&RE, "RIGHT_PAREN", offset) {
                None => Err(self.unbalanced_parentheses(offset)),
                Some(matched) => Ok(matched),
            }
        }

        fn newline(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^(\n+)[ \t]*"));
            self.terminal(&RE, "NEWLINE", offset)
        }

        fn element_t(&self, command: &BlockCommand, offset: usize) -> Result<Option<Match>, Error> {
            self.command_element_t(&command.re, true, offset)
        }

        fn block_body(
            &self,
            end_command: &BlockCommand,
            mut offset: usize,
        ) -> Result<Option<Match>, Error> {
            if let Some((_, new_offset)) = self.newline_or_gap(offset) {
                offset = new_offset;
            }

            let mut result: Vec<Node> = vec![];
            let mut last_newline_or_gap: Option<Node> = None;
            loop {
                if self.element_t(end_command, offset)?.is_some() {
                    break;
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
                        offset = new_offset
                    }
                    None => {
                        return Ok(Some((tree("block_body", result), offset)));
                    }
                }
            }

            Ok(Some((tree("block_body", result), offset)))
        }

        fn block_t(
            &self,
            start_command: &BlockCommand,
            end_command: &BlockCommand,
            offset: usize,
        ) -> Result<Option<Match>, Error> {
            match self.element_t(start_command, offset)? {
                None => Ok(None),
                Some((matched_start, offset)) => match self.block_body(end_command, offset)? {
                    None => Err(self.unbalanced_block(offset)),
                    Some((matched_body, offset)) => match self.element_t(end_command, offset)? {
                        None => Err(self.unbalanced_block(offset)),
                        Some((matched_end, offset)) => Ok(Some((
                            tree("block", vec![matched_start, matched_body, matched_end]),
                            offset,
                        ))),
                    },
                },
            }
        }

        fn block(&self, offset: usize) -> Result<Option<Match>, Error> {
            for (block_start, block_end) in &self.blocks {
                if let Some(matched) = self.block_t(block_start, block_end, offset)? {
                    return Ok(Some(matched));
                }
            }

            Ok(None)
        }

        fn commented_argument_atom(
            &self,
            offset: usize,
        ) -> Result<Option<(Vec<Node>, usize)>, Error> {
            if let Some((matched, offset)) = self.bracket_comment(offset)? {
                return Ok(Some((vec![matched], offset)));
            }

            if let Some((matched_comment, offset)) = self.line_comment(offset) {
                if let Some((matched_newline, offset)) = self.newline(offset) {
                    return Ok(Some((vec![matched_comment, matched_newline], offset)));
                }
            }

            Ok(None)
        }

        fn bracket_argument(&self, offset: usize) -> Result<Option<Match>, Error> {
            Ok(self
                .bracket_argument_token(offset)?
                .map(|(matched, offset)| (tree("bracket_argument", vec![matched]), offset)))
        }

        fn quotation_mark(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r#"^(")"#));
            self.terminal(&RE, "QUOTATION_MARK", offset)
        }

        fn quoted_argument(&self, offset: usize) -> Result<Option<Match>, Error> {
            static RE: LazyLock<Regex> = LazyLock::new(|| {
                regex(add_ignores(quoted_argument_pattern().to_string()).as_str())
            });
            match RE.captures(&self.text[offset..]) {
                None => match self.quotation_mark(offset) {
                    None => Ok(None),
                    Some(_) => Err(self.generic_parsing_error(offset)),
                },
                Some(captures) => Ok(captures.get(1).map(|matched| {
                    (
                        tree(
                            "quoted_argument",
                            vec![token("QUOTED_ARGUMENT", matched.as_str())],
                        ),
                        offset + captures.get_match().len(),
                    )
                })),
            }
        }

        fn unquoted_argument(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(unquoted_argument_pattern()));
            match RE.captures(&self.text[offset..]) {
                None => None,
                Some(captures) => captures.get(1).map(|matched| {
                    (
                        tree(
                            "unquoted_argument",
                            vec![token("UNQUOTED_ARGUMENT", matched.as_str())],
                        ),
                        offset + captures.get_match().len(),
                    )
                }),
            }
        }

        fn complex_argument(&self, offset: usize) -> Result<Option<Match>, Error> {
            Ok(match self.left_paren(offset) {
                None => None,
                Some((_, offset)) => match self.arguments(offset)? {
                    None => None,
                    Some((matched_arguments, offset)) => {
                        let (_, offset) = self.right_paren(offset)?;
                        Some((tree("complex_argument", vec![matched_arguments]), offset))
                    }
                },
            })
        }

        fn argument(&self, offset: usize) -> Result<Option<Match>, Error> {
            if let Some(matched) = self.bracket_argument(offset)? {
                return Ok(Some(matched));
            }

            if let Some(matched) = self.quoted_argument(offset)? {
                return Ok(Some(matched));
            }

            if let Some(matched) = self.unquoted_argument(offset) {
                return Ok(Some(matched));
            }

            self.complex_argument(offset)
        }

        fn commented_argument(&self, offset: usize) -> Result<Option<Match>, Error> {
            Ok(match self.argument(offset)? {
                None => None,
                Some((matched_argument, offset)) => match self.commented_argument_atom(offset)? {
                    None => Some((matched_argument, offset)),
                    Some((mut nodes, offset)) => {
                        nodes.push(matched_argument);
                        nodes.rotate_right(1);
                        Some((tree("commented_argument", nodes), offset))
                    }
                },
            })
        }

        fn separation(&self, offset: usize) -> Result<Option<SkippableMatch>, Error> {
            if let Some((node, offset)) = self.bracket_comment(offset)? {
                return Ok(Some((Some(node), offset)));
            }

            if let Some((node, offset)) = self.line_comment(offset) {
                return Ok(Some((Some(node), offset)));
            }

            if let Some((_, offset)) = self.newline(offset) {
                return Ok(Some((None, offset)));
            }

            Ok(None)
        }

        fn arguments_atom(&self, offset: usize) -> Result<Option<SkippableMatch>, Error> {
            if let Some((node, offset)) = self.commented_argument(offset)? {
                return Ok(Some((Some(node), offset)));
            }

            if let Some(matched) = self.separation(offset)? {
                return Ok(Some(matched));
            }

            Ok(None)
        }

        fn arguments(&self, mut offset: usize) -> Result<Option<Match>, Error> {
            let mut result = Vec::<Node>::new();
            while let Some((matched, new_offset)) = self.arguments_atom(offset)? {
                if let Some(matched) = matched {
                    result.push(matched);
                }
                offset = new_offset;
            }
            Ok(Some((tree("arguments", result), offset)))
        }

        fn indentation(&self, offset: usize) -> Node {
            let start = match self.text[..offset].rfind('\n') {
                Some(value) => value + 1,
                None => 0usize,
            };
            token("ANONYMOUS", &self.text[start..offset])
        }

        fn formatted_node(&self, start: usize, end: usize) -> Node {
            let value = if start >= end {
                ""
            } else {
                &self.text[start + 1..end]
            };
            tree("formatted_node", vec![token("ANONYMOUS", value)])
        }

        fn create_command_invocation_node(
            &self,
            identifier: Node,
            arguments: Node,
            initial_offset: usize,
            custom_formatting_start: usize,
            custom_formatting_end: usize,
        ) -> Node {
            match &identifier {
                Node::Token { type_: _, value } => {
                    if self.is_known_command(value) {
                        tree("command_invocation", vec![identifier, arguments])
                    } else {
                        tree(
                            "custom_command",
                            vec![
                                self.indentation(initial_offset),
                                identifier,
                                arguments,
                                self.formatted_node(custom_formatting_start, custom_formatting_end),
                            ],
                        )
                    }
                }
                _ => tree("command_invocation", vec![identifier, arguments]),
            }
        }

        fn identifier(&self, re: &regex::Regex, offset: usize, block_edge: bool) -> Option<Match> {
            match self.terminal(re, "IDENTIFIER", offset) {
                None => None,
                Some((node, offset)) => match node {
                    Node::Token {
                        type_: _,
                        value: ref command_name,
                    } => {
                        if block_edge || !self.is_block_edge_command(command_name.as_str()) {
                            return Some((node, offset));
                        }

                        None
                    }
                    Node::Tree {
                        data: _,
                        children: _,
                    } => Some((node, offset)),
                },
            }
        }

        fn command_invocation_t(
            &self,
            re: &regex::Regex,
            offset: usize,
            block_edge: bool,
        ) -> Result<Option<Match>, Error> {
            let initial_offset = offset;
            Ok(match self.identifier(re, offset, block_edge) {
                None => None,
                Some((matched_identifier, identifier_offset)) => {
                    match self.left_paren(identifier_offset) {
                        None => None,
                        Some((_, offset)) => match self.arguments(offset)? {
                            None => None,
                            Some((matched_arguments, arguments_offset)) => {
                                let (_, offset) = self.right_paren(arguments_offset)?;
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
            block_edge: bool,
            offset: usize,
        ) -> Result<Option<Match>, Error> {
            Ok(match self.command_invocation_t(re, offset, block_edge)? {
                None => None,
                Some((matched, offset)) => match self.line_comment(offset) {
                    None => {
                        if block_edge {
                            Some((tree("command_element", vec![matched]), offset))
                        } else {
                            Some((matched, offset))
                        }
                    }
                    Some((matched_comment, new_offset)) => Some((
                        tree("command_element", vec![matched, matched_comment]),
                        new_offset,
                    )),
                },
            })
        }

        fn command_element(&self, offset: usize) -> Result<Option<Match>, Error> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(IDENTIFIER_R));
            self.command_element_t(&RE, false, offset)
        }

        fn standalone_identifier(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(IDENTIFIER_R));
            self.terminal(&RE, "IDENTIFIER", offset)
                .map(|(node, offset)| (tree("standalone_identifier", vec![node]), offset))
        }

        fn bracket_comment(&self, mut offset: usize) -> Result<Option<Match>, Error> {
            let mut result = Vec::<Node>::new();
            if let Some((matched, new_offset)) = self.pound_sign(offset) {
                result.push(matched);
                offset = new_offset;
            } else {
                return Ok(None);
            }

            if let Some((matched, new_offset)) = self.bracket_argument_token(offset)? {
                result.push(matched);
                offset = new_offset;
                return Ok(Some((tree("bracket_comment", result), offset)));
            }

            Ok(None)
        }

        fn line_comment(&self, mut offset: usize) -> Option<Match> {
            let mut result = Vec::<Node>::new();
            if let Some((matched, new_offset)) = self.pound_sign(offset) {
                result.push(matched);
                offset = new_offset;
            } else {
                return None;
            }

            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^[^\n]+"));
            if let Some(matched) = RE.find(&self.text[offset..]) {
                result.push(token("LINE_COMMENT_CONTENT", matched.as_str()));
                offset += matched.len();
            }

            Some((tree("line_comment", result), offset))
        }

        fn non_command_element(&self, mut offset: usize) -> Result<Option<Match>, Error> {
            let mut result = Vec::<Node>::new();
            while let Some((matched, new_offset)) = self.bracket_comment(offset)? {
                result.push(matched);
                offset = new_offset;
            }

            if let Some((matched, new_offset)) = self.line_comment(offset) {
                result.push(matched);
                offset = new_offset;
            }

            if result.is_empty() {
                return Ok(None);
            }

            Ok(Some((tree("non_command_element", result), offset)))
        }

        fn file_element(&self, offset: usize) -> Result<Option<Match>, Error> {
            if let Some(result) = self.block(offset)? {
                return Ok(Some(result));
            }

            if let Some(result) = self.command_element(offset)? {
                return Ok(Some(result));
            }

            if let Some(result) = self.standalone_identifier(offset) {
                return Ok(Some(result));
            }

            if let Some(result) = self.non_command_element(offset)? {
                return Ok(Some(result));
            }

            Ok(None)
        }

        fn newline_or_gap(&self, offset: usize) -> Option<Match> {
            static RE: LazyLock<Regex> = LazyLock::new(|| regex(r"^(\n[ \t]*)(\n[ \t]*)*"));
            match RE.captures(&self.text[offset..]) {
                None => None,
                Some(captures) => match captures.get(2) {
                    None => Some((token("NEWLINE", "\n"), offset + captures.get_match().len())),
                    Some(_) => Some((
                        token("NEWLINE", "\n\n"),
                        offset + captures.get_match().len(),
                    )),
                },
            }
        }

        fn start(&self) -> Result<Node, Error> {
            let mut offset = match self.newline_or_gap(0) {
                Some((_, new_offset)) => new_offset,
                None => 0usize,
            };
            let mut result: Vec<Node> = vec![];
            let mut last_newline_or_gap: Option<Node> = None;

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
                        offset = new_offset
                    }
                    None => {
                        break;
                    }
                }
            }

            if offset != self.text.len() {
                let (_, offset) = self.right_paren(offset)?;
                return Err(self.unbalanced_parentheses(offset));
            }

            Ok(tree("start", result))
        }

        fn is_known_command(&self, command_name: &str) -> bool {
            let command_name = command_name.to_lowercase();
            self.known_commands
                .iter()
                .any(|item| item.as_str() == command_name)
        }

        fn is_block_edge_command(&self, command_name: &str) -> bool {
            let name = command_name.to_lowercase();
            self.blocks
                .iter()
                .any(|(start, end)| start.name == name || end.name == name)
        }
    }

    type BlockDefinition = (String, String);
    type BlockDefinitions = Vec<BlockDefinition>;

    fn block_command(name: String) -> BlockCommand {
        let pattern = format!("(?i)^({})[ \t]*", name);
        let re = regex(pattern.as_str());
        BlockCommand { name, re }
    }

    fn prepare_blocks(blocks: BlockDefinitions) -> Vec<(BlockCommand, BlockCommand)> {
        blocks
            .into_iter()
            .map(|(start, end)| (block_command(start), block_command(end)))
            .collect()
    }

    #[pyfunction]
    fn parse(
        text: String,
        blocks: BlockDefinitions,
        known_commands: Vec<String>,
    ) -> PyResult<ParsingResult> {
        let parser = Parser {
            blocks: prepare_blocks(blocks),
            known_commands,
            text,
        };

        Ok(match parser.start() {
            Ok(node) => ParsingResult::Success(node),
            Err(Error {
                error_type,
                explanation,
                line,
                column,
            }) => ParsingResult::Fail {
                error_type,
                explanation,
                line,
                column,
            },
        })
    }
}
