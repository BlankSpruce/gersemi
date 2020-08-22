class ASTMismatch(Exception):
    pass


class ParsingError(SyntaxError):
    description: str = ""

    def __str__(self):
        context, line, column = self.args  # pylint: disable=unbalanced-tuple-unpacking
        return f"{line}:{column}: {self.description}\n{context}"


class GenericParsingError(ParsingError):
    description = "unspecified parsing error"


class UnbalancedParentheses(ParsingError):
    description = "unbalanced parentheses"


class UnbalancedBrackets(ParsingError):
    description = "unbalanced brackets"
