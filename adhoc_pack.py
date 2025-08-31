

# ---------------------------------------------------------------------------------------------------------------
#  Class Pack RReg
# ---------------------------------------------------------------------------------------------------------------
class RRegPack():
    def __init__(self,source_node, target_node):
        self.type = 'rreg'
        self.source_node= source_node
        self.target_node = target_node
        self.path = [source_node]
        self.start_time = 0
        self.current_node = source_node
        self.size_was_sent = 0

    # -------------------------------------------------
    def get_next_hop(self):
        return self.path[-1]

    # -------------------------------------------------
    def get_size(self):
        return 20 + len(self.path) * 4

    # -------------------------------------------------
    def add_node(self, node_id):
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
class RRepPack():
    def __init__(self,path):
        self.type = 'rrep'
        self.path = path
        self.add_information = []
        self.start_time = 0
        self.current_node = path[-3]
        self.size_was_sent = 0

    # -------------------------------------------------
    def get_next_hop(self):
        index = self.path.index(self.current_node)
        return self.path[index -1]

    # -------------------------------------------------
    def get_size(self):
        return 20 + len(self.path) * 4 + len(self.add_information) * 4

    # -------------------------------------------------
    def add_connect_inform(self, value):
        self.add_information.append(value)
    # -------------------------------------------------
    def set_current_node(self, node_id):
        self.current_node = node_id
        return

    # -------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------
#  Class Pack Data
# ---------------------------------------------------------------------------------------------------------------
class DataPack():
    def __init__(self,target_node, data_size):
        self.type = 'data'
        self.target_node = target_node
        self.path = []
        self.size = data_size
        self.size_was_sent = 0
        self.start_time = 0
        self.current_node = -1
        self.id = 0

    # -------------------------------------------------
    def get_size(self):
        return 20 + len(self.path) * 4 + self.size

    # -------------------------------------------------
    def set_current_node(self, node_id):
        self.current_node = node_id
        return

    # -------------------------------------------------
    def get_next_hop(self):
        if len(self.path) > 0:
            index = self.path.index(self.current_node)
            return self.path[index + 1]
        else:
            return -1

    # -------------------------------------------------

