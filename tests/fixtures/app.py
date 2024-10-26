from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
from typing import Optional, Union
from tests.utils import preprocess


def repr_outcome(outcome):
    return f"""- returncode: {outcome.returncode}
----------------------------------------
- stdout:
{preprocess(str(outcome.stdout)) if outcome.stdout is not None else "--ignore--"}
----------------------------------------
- stderr:
{preprocess(str(outcome.stderr)) if outcome.stderr is not None else "--ignore--"}"""


@dataclass
class ActualOutcome:
    returncode: int
    stdout: str
    stderr: str

    def __repr__(self):
        return f"""Actual outcome:
{repr_outcome(self)}"""


class Matcher:
    def __init__(self, matcher, describe):
        self.matcher = matcher
        self.describe = describe

    def __eq__(self, other):
        return self.matcher(other)

    def __repr__(self):
        return f"Match({self.describe})"


def match_not(thing):
    return Matcher(thing.__ne__, f"not {repr(thing)}")


@dataclass
class ExpectedOutcome:
    returncode: int
    stdout: Optional[Union[str, Matcher]] = None
    stderr: Optional[Union[str, Matcher]] = None

    def __eq__(self, other):
        if not isinstance(other, ActualOutcome):
            raise NotImplementedError

        result = other.returncode == self.returncode
        if self.stdout is not None:
            result = result and other.stdout == self.stdout

        if self.stderr is not None:
            result = result and other.stderr == self.stderr

        return result

    def __repr__(self):
        return f"""Expected outcome:
{repr_outcome(self)}"""


def outcome(completed_process):
    return ActualOutcome(
        returncode=completed_process.returncode,
        stdout=completed_process.stdout,
        stderr=completed_process.stderr,
    )


HERE = Path(os.path.dirname(os.path.realpath(__file__)))


class App:
    def __init__(self, cache, fallback_cwd):
        self.cache = cache
        self.fallback_cwd = fallback_cwd

    def __call__(self, *args, **kwargs):
        if "cwd" not in kwargs:
            kwargs["cwd"] = self.fallback_cwd

        kwargs["input"] = str(self.cache) + "\n" + kwargs.get("input", "")

        return outcome(
            subprocess.run(
                [sys.executable, HERE / "patched_gersemi", *map(str, args)],
                check=False,
                encoding="utf8",
                text=True,
                capture_output=True,
                **kwargs,
            )
        )


def success(stdout=None, stderr=None):
    return ExpectedOutcome(returncode=0, stdout=stdout, stderr=stderr)


def fail(stdout=None, stderr=None):
    return ExpectedOutcome(returncode=1, stdout=stdout, stderr=stderr)
