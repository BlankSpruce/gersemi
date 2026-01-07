# pylint: disable=redefined-outer-name
import os
import shutil
import subprocess
import pytest
from tests.fixtures.app import fail, Matcher, reformatted, success


IGNORE_FILES = (".ignore", ".gitignore", ".git/info/exclude")


@pytest.fixture
def testdir(testfiles):
    return (testfiles / "directory_with_some_not_formatted_files").resolve()


class Repo(os.PathLike):
    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return str(self.path)

    def __str__(self):
        return str(self.path)

    @property
    def bad1(self):
        return (self.path / "not_formatted_file1.cmake").resolve()

    @property
    def bad2(self):
        return (self.path / "not_formatted_file2.cmake").resolve()

    @property
    def bad3(self):
        return (self.path / "not_formatted_file3.cmake").resolve()

    def gitignore(self, content):
        with open(self.path / ".gitignore", "w", encoding="utf-8") as f:
            f.write(content)

    def named_ignore_file(self, name, content):
        with open(self.path / name, "w", encoding="utf-8") as f:
            f.write(content)


@pytest.fixture
def not_initialized_repo(testdir):
    return Repo(testdir)


@pytest.fixture
def repo(not_initialized_repo):
    subprocess.check_call(["git", "init", "-q"], cwd=not_initialized_repo)
    return not_initialized_repo


def test_gersemi_git_just_works(app, repo):
    assert app("--check", ".", cwd=repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )


def test_gitignore_empty(app, repo):
    repo.gitignore("")

    assert app("--check", ".", cwd=repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )


@pytest.mark.parametrize("ignore_file", IGNORE_FILES)
def test_ignore_file_bad1_and_bad3_ignored(app, repo, ignore_file):
    repo.named_ignore_file(
        ignore_file,
        """
not_formatted_file1*
not_formatted_file3*
        """,
    )

    assert app("--check", ".", cwd=repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad2),
    )


@pytest.mark.parametrize("ignore_file", IGNORE_FILES)
def test_dont_respect_ignore_files(app, repo, ignore_file):
    repo.named_ignore_file(
        ignore_file,
        """
not_formatted_file1*
not_formatted_file3*
        """,
    )

    assert app("--no-respect-ignore-files", "--check", ".", cwd=repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )


def test_gitignore_all_bad_ignored(app, repo):
    repo.gitignore(
        """
not_formatted_file*
        """
    )

    assert app("--check", ".", cwd=repo) == success(stdout="", stderr="")


def test_formatting_of_explicitly_mentioned_ignored_files_fails(app, repo):
    assert app("--check", repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )
    assert app("--check", repo.bad1, repo.bad2, repo.bad3) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )

    repo.gitignore(
        """
not_formatted_file1*
        """
    )

    assert app("--check", repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad2, repo.bad3),
    )
    assert app("--check", repo.bad1, repo.bad2, repo.bad3) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )

    repo.gitignore(
        """
not_formatted_file*
        """
    )
    assert app("--check", repo) == success(stdout="", stderr="")
    assert app("--check", repo.bad1, repo.bad2, repo.bad3) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )


def starts_with(s):
    return Matcher(
        matcher=lambda inp: inp.startswith(s),
        describe=f'Starts with: "{s}"',
    )


def test_gersemi_in_non_git_repository(app, not_initialized_repo):
    assert app("--check", ".", cwd=not_initialized_repo) == fail(
        stdout="",
        stderr=reformatted(
            not_initialized_repo.bad1,
            not_initialized_repo.bad2,
            not_initialized_repo.bad3,
        ),
    )

    not_initialized_repo.gitignore(
        """
not_formatted_file*
        """
    )

    assert app("--check", ".", cwd=not_initialized_repo) == success(
        stdout="", stderr=""
    )


def test_whitespace_in_filename(app, repo):
    bad4 = (repo.path / "not formatted file 4.cmake").resolve()
    shutil.copy(repo.bad3, bad4)

    assert app("--check", repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3, bad4),
    )

    repo.gitignore(
        """
not formatted file*
        """
    )

    assert app("--check", repo) == fail(
        stdout="",
        stderr=reformatted(repo.bad1, repo.bad2, repo.bad3),
    )


@pytest.fixture
def second_repo(repo):
    result = repo.path.with_name(repo.path.name + "_2")
    assert str(repo) < str(result)

    shutil.copytree(repo, result)
    return Repo(result)


def test_multiple_repositories_in_single_invocation(app, repo, second_repo, testfiles):
    assert app("--check", repo, second_repo) == fail(
        stdout="",
        stderr=reformatted(
            repo.bad1,
            repo.bad2,
            repo.bad3,
            second_repo.bad1,
            second_repo.bad2,
            second_repo.bad3,
        ),
    )

    repo.gitignore(
        """
not_formatted_file1*
not_formatted_file2*
        """
    )
    second_repo.gitignore(
        """
not_formatted_file3*
not_formatted_file2*
        """
    )

    assert app("--check", repo, second_repo) == fail(
        stdout="",
        stderr=reformatted(
            repo.bad3,
            second_repo.bad1,
        ),
    )

    with open(testfiles / ".ignore", "w", encoding="utf-8") as f:
        f.write(
            """
not_formatted_file*
            """
        )

    assert app("--check", repo, second_repo) == success(stdout="", stderr="")
