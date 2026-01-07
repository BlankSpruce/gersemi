import pytest
from gersemi.configuration import LineRange, line_ranges

valid_line_ranges = [
    (
        "123-456",
        (LineRange(123, 456),),
    ),
    (
        "123-456,789-901",
        (LineRange(123, 456), LineRange(789, 901)),
    ),
    (
        "123-456,789-901,2345-6789",
        (LineRange(123, 456), LineRange(789, 901), LineRange(2345, 6789)),
    ),
    (
        ",123-456",
        (LineRange(123, 456),),
    ),
    (
        ",123-456,",
        (LineRange(123, 456),),
    ),
    (
        ",123-456,,",
        (LineRange(123, 456),),
    ),
    (
        "123-456,,789-901,,,2345-6789",
        (LineRange(123, 456), LineRange(789, 901), LineRange(2345, 6789)),
    ),
]


@pytest.mark.parametrize(
    ("given", "expected"),
    valid_line_ranges,
    ids=[given for given, _ in valid_line_ranges],
)
def test_valid_line_range(given, expected):
    assert line_ranges(given) == expected


invalid_line_ranges = [
    ("123-", "123-"),
    ("-456", "-456"),
    ("123-456,789-,901-2345", "789-"),
    ("123-456;789-901", "123-456;789-901"),
    ("123-456/789-901", "123-456/789-901"),
    ("456-123", "456-123"),
]


@pytest.mark.parametrize(
    ("given", "warning"),
    invalid_line_ranges,
    ids=[given for given, _ in invalid_line_ranges],
)
def test_invalid_line_range(given, warning):
    with pytest.raises(Exception, match=warning):
        line_ranges(given)
