# pylint: disable=attribute-defined-outside-init
from io import BytesIO
from lark import Lark
from lark.grammar import Rule
from lark.lark import LarkOptions
from lark.lexer import TerminalDef
from lark.utils import SerializeMemoizer
from gersemi.parsing_transformer import ParsingTransformer


class PickleBeforeLark0dot8dot6:
    # similar function available since lark 0.8.6
    def _recreate_lark_parser(self, data, memo):
        # pylint: disable=protected-access
        deserialized_memo = SerializeMemoizer.deserialize(
            memo, {"Rule": Rule, "TerminalDef": TerminalDef}, {}
        )
        instance = Lark.__new__(Lark)
        options = dict(data["options"])
        options["transformer"] = ParsingTransformer()
        instance.options = LarkOptions.deserialize(options, deserialized_memo)
        instance.rules = [
            Rule.deserialize(rule, deserialized_memo) for rule in data["rules"]
        ]
        instance._prepare_callbacks()
        instance.parser = instance.parser_class.deserialize(
            data["parser"],
            deserialized_memo,
            instance._callbacks,
            instance.options.postlex,
        )
        return instance

    def __getstate__(self):
        return self.lark_parser.memo_serialize([TerminalDef, Rule])

    def __setstate__(self, state):
        data, memo = state
        self.lark_parser = self._recreate_lark_parser(data, memo)


class PickleAfterLark0dot8dot6:
    def __getstate__(self) -> bytes:
        state = BytesIO()
        self.lark_parser.save(state)
        return state.getvalue()

    def __setstate__(self, state: bytes):
        state_as_file = BytesIO(state)
        self.lark_parser = Lark.load(state_as_file)
