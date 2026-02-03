import pytest
from framework.graph.node import SharedMemory

def test_shared_memory_permissions_enforced():
    mem = SharedMemory()
    scoped = mem.with_permissions(read_keys=["a"], write_keys=["b"])

    # Allowed write
    scoped.write("b", 123)

    # Disallowed write
    with pytest.raises(PermissionError):
        scoped.write("c", 456)

    # Allowed read key returns None if unset
    assert scoped.read("a") is None

    # Disallowed read should raise
    with pytest.raises(PermissionError):
        scoped.read("c")
