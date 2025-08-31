from typing import Literal, Any
from abc import ABC, abstractmethod

PackType = Literal[
    "rreg",
    "rrep",
    "data",
]


# ---------------------------------------------------------------------------------------------------------------
# Base Class for Packets
# ---------------------------------------------------------------------------------------------------------------
class BasePack(ABC):
    def __init__(self, pack_type: PackType):
        self.type: PackType = pack_type
        self.path: list[int] = []
        self.start_time: int = 0
        self.current_node_id: int = -1
        self.size_was_sent: int = 0

    @abstractmethod
    def get_size(self) -> int:
        """Calculate the size of the packet."""
        pass

    @abstractmethod
    def get_next_hop(self) -> int | None:
        """Determine the next hop in the path."""
        pass

    def set_current_node(self, node_id: int) -> None:
        """Set the current node ID."""
        self.current_node_id = node_id


# ---------------------------------------------------------------------------------------------------------------
# Class Pack RReg represent Route Request DSR packet
# ---------------------------------------------------------------------------------------------------------------
class RRegPack(BasePack):
    def __init__(self, source_node_id: int, target_node_id: int):
        super().__init__("rreg")
        self.source_node_id: int = source_node_id
        self.target_node_id: int = target_node_id
        self.path: list[int] = [source_node_id]
        self.current_node_id: int = source_node_id

    def get_next_hop(self) -> int:
        return self.path[-1]

    def get_size(self) -> int:
        return 20 + len(self.path) * 4

    def add_node(self, node_id: int) -> bool:
        if node_id in self.path:
            return False
        self.path.append(node_id)
        return True


# ---------------------------------------------------------------------------------------------------------------
# Class Pack RRep represet Route Response DSR packet
# ---------------------------------------------------------------------------------------------------------------
class RRepPack(BasePack):
    def __init__(self, path: list[int]):
        super().__init__("rrep")
        self.path: list[int] = path
        self.add_information: list[Any] = []
        self.current_node_id: int = path[-3] if len(path) >= 3 else -1

    def get_next_hop(self) -> int:
        index = self.path.index(self.current_node_id)
        return self.path[index - 1]

    def get_size(self) -> int:
        return 20 + len(self.path) * 4 + len(self.add_information) * 4

    def add_connect_inform(self, value: Any) -> None:
        self.add_information.append(value)


# ---------------------------------------------------------------------------------------------------------------
# Class Pack Data represent some IP packet with payload
# ---------------------------------------------------------------------------------------------------------------
class DataPack(BasePack):
    def __init__(self, target_node_id: int, data_size: int):
        super().__init__("data")
        self.target_node_id: int = target_node_id
        self.size: int = data_size
        self.id: int = 0

    def get_size(self) -> int:
        return 20 + len(self.path) * 4 + self.size

    def get_next_hop(self) -> int | None:
        if len(self.path) > 0:
            index = self.path.index(self.current_node_id)
            if index + 1 < len(self.path):
                return self.path[index + 1]
        return -1
