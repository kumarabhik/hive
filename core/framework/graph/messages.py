from dataclasses import dataclass
from typing import Any

@dataclass
class NodeMessage:
    from_node: str
    to_node: str
    payload: dict[str, Any]
