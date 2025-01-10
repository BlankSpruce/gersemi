from collections import abc


class ImmutableDict(abc.Mapping):
    def __init__(self, d):
        self._d = d

    def __getitem__(self, key):
        return self._d[key]

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __contains__(self, item):
        return item in self._d

    def __hash__(self):
        return hash(frozenset(self._d.items()))


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
