import os
import lark


def create_parser():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    return lark.Lark.open(
        grammar_filename=os.path.join(this_file_dir, "cmake.lark"),
        parser="lalr",
        propagate_positions=True,
        maybe_placeholders=False,
    )
