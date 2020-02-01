from typing import Any, Iterator, List


def pop_all(in_list: List) -> List:
    popped, in_list[:] = in_list[:], []
    return popped


def advance(iterator: Iterator, times: int, default: Any) -> Any:
    result = default
    for _ in range(times):
        new_result = next(iterator, default)
        if new_result == default:
            break
        result = new_result
    return result
