from collections import abc


class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise TypeError("mutation not allowed")

    def __delitem__(self, key):
        raise TypeError("mutation not allowed")

    def __hash__(self):
        return hash(frozenset(self.items()))


def make_immutable(thing):
    if isinstance(thing, abc.Mapping):
        return ImmutableDict(
            {key: make_immutable(value) for key, value in thing.items()}
        )

    if isinstance(thing, str):
        return thing

    if isinstance(thing, abc.Collection):
        return tuple(map(make_immutable, thing))

    return thing
