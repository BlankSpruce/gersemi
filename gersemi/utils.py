from typing import List


def pop_all(in_list: List) -> List:
    popped, in_list[:] = in_list[:], []
    return popped
