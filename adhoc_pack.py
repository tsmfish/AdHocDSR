from typing import Literal, Any

PackType = Literal[
    "rreg",
    "rrep",
    "data",
]


# ---------------------------------------------------------------------------------------------------------------
#  Class Pack RReg
# ---------------------------------------------------------------------------------------------------------------
class RRegPack:
    def __init__(self, source_node_id: int, target_node_id: int):
        self.type: PackType = "rreg"
        self.source_node: int = source_node_id
        self.target_node: int = target_node_id
        self.path: list[int] = [source_node_id]
        self.start_time: int = 0
        self.current_node: int = source_node_id
        self.size_was_sent: int = 0

    # -------------------------------------------------
    def get_next_hop(self) -> int:
        return self.path[-1]

    # -------------------------------------------------
    def get_size(self) -> int:
        return 20 + len(self.path) * 4

    # -------------------------------------------------
    def add_node(self, node_id) -> bool:
        if node_id in self.path:
            return False
        else:
            self.path.append(node_id)
            return True

    # -------------------------------------------------
    def set_current_node(self, node_id):
        return


# ---------------------------------------------------------------------------------------------------------------
#  Class Pack RRep
# ---------------------------------------------------------------------------------------------------------------
class RRepPack:
    def __init__(self, path: list[int]):
        self.type: PackType = "rrep"
        self.path: list[int] = path
        self.add_information: list[Any] = []
        self.start_time: int = 0
        self.current_node: int = path[-3]
        self.size_was_sent: int = 0

    # -------------------------------------------------
    def get_next_hop(self) -> int:
        index = self.path.index(self.current_node)
        return self.path[index - 1]

    # -------------------------------------------------
    def get_size(self) -> int:
        return 20 + len(self.path) * 4 + len(self.add_information) * 4

    # -------------------------------------------------
    def add_connect_inform(self, value: Any):
        self.add_information.append(value)

    # -------------------------------------------------
    def set_current_node(self, node_id):
        self.current_node = node_id
        return

    # -------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------
#  Class Pack Data
# ---------------------------------------------------------------------------------------------------------------
class DataPack:
    def __init__(self, target_node_id: int, data_size: int):
        self.type: PackType = "data"
        self.target_node: int = target_node_id
        self.path: list[int] = []
        self.size: int = data_size
        self.size_was_sent: int = 0
        self.start_time: int = 0
        self.current_node: int = -1
        self.id: int = 0

    # -------------------------------------------------
    def get_size(self) -> int:
        return 20 + len(self.path) * 4 + self.size

    # -------------------------------------------------
    def set_current_node(self, node_id) -> None:
        self.current_node = node_id
        return

    # -------------------------------------------------
    def get_next_hop(self) -> int | None:
        if len(self.path) > 0:
            index = self.path.index(self.current_node)
            return self.path[index + 1]
        else:
            return -1

    # -------------------------------------------------
