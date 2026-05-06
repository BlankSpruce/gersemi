import pickle
import pytest
from gersemi.immutable import ImmutableDict, make_immutable


def test_immutable_dict_can_be_unpickled():
    data = make_immutable({"outer": {"inner": ["value"]}})

    restored = pickle.loads(pickle.dumps(data))

    assert isinstance(restored, ImmutableDict)
    assert isinstance(restored["outer"], ImmutableDict)
    assert dict(restored) == dict(data)
    with pytest.raises(TypeError, match="mutation not allowed"):
        restored["another"] = "value"
