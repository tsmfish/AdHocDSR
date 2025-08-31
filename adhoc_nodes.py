import random
from copy import deepcopy
import adhoc_pack
from adhoc_pack import RRegPack


# ---------------------------------------------------------------------------------------------------------------
#  Class connection
# ---------------------------------------------------------------------------------------------------------------
class AdHocConnect:
    def __init__(self, pointer_node1, pointer_node2):
        self.nodes_pointers = [pointer_node1, pointer_node2]
        self.default_bit_rate_error = 0.01
        self.current_bit_rate_error = 0.01
        self.snr = 2
        self.flag_work = True
        self.default_byte_per_tik = 10000
        self.current_byte_per_tik = 10000
        self.sent_byte_in_current_tic = 0
        # self.sent_byte_in_current_tic_to_back = 0

    # ---------------------------------------------------------------------------------------------------------------
    def get_nodes(self):
        return self.nodes_pointers[0], self.nodes_pointers[1]

    # ---------------------------------------------------------------------------------------------------------------
    def get_quality_param(self):
        return self.snr

    # ---------------------------------------------------------------------------------------------------------------
    def send_one_tik_part(self):
        self._send_one_tik_part(
            source_node=self.nodes_pointers[0], target_node=self.nodes_pointers[1]
        )
        self._send_one_tik_part(
            source_node=self.nodes_pointers[1], target_node=self.nodes_pointers[0]
        )

    # ---------------------------------------------------------------------------------------------------------------
    def _send_one_tik_part(self, source_node, target_node):
        non_send_pack = []
        if source_node.node_id == 12:
            print("Test")
        for pack in source_node.queue_to_send:
            if pack.get_next_hop() == target_node.node_id:
                pack.size_was_sent += self._try_to_send_pack(pack)
                if pack.size_was_sent == pack.get_size():
                    target_node.queue_receiving.append(pack)
                    continue
            non_send_pack.append(pack)

        source_node.queue_to_send = non_send_pack

    # ---------------------------------------------------------------------------------------------------------------
    def _try_to_send_pack(self, pack):
        size = pack.get_size()
        part_size = 100
        if size < part_size:
            part_size = size
        total_send = 0
        while (
            self.current_byte_per_tik > self.sent_byte_in_current_tic + part_size
        ) and total_send < size:
            self.sent_byte_in_current_tic += part_size
            if not self._check_error(size):
                total_send += size

        return total_send

    # ---------------------------------------------------------------------------------------------------------------
    def _check_error(self, size):
        return False

    # ---------------------------------------------------------------------------------------------------------------
    def send_pack(self, pack_length_in_byte):
        return self._use_snr(pack_length_in_byte)

        # threshold = self.bit_rate_error
        # # кількість помилок
        # threshold = threshold**2
        #
        # threshold = 10000* threshold + 1
        # for xx in range(0,pack_lendth_in_byte, 100):
        #     if threshold > random.randint(0, 10000):
        #         return False
        # return True

    # ----------------------------------------------
    def _use_snr(self, pack_length_in_byte):
        threshold = 10000 * (
            (1 - (1 / (1 + 2.71818281828 ** (-self.snr)))) ** 2
        ) + random.randint(1, 4)
        for xx in range(0, pack_length_in_byte, 100):
            if threshold > random.randint(0, 10000):
                return False
        return True

    # ----------------------------------------------
    def get_other_node(self, my_id):
        if my_id == self.nodes_pointers[0].node_id:
            return self.nodes_pointers[1]
        return self.nodes_pointers[0]


# ---------------------------------------------------------------------------------------------------------------
#  Class  ad_hoc node
# --------------------------------------------------------------------------------------------------------------
class AdHocNode:
    def __init__(self, node_id, y, x, model_air):
        self.node_id = node_id
        self.position_x = x
        self.position_y = y
        self.connect_list = []
        self.flag_work = True
        self.__conection_count = 3
        self.model_air = model_air
        self.queue_to_send = []
        self.queue_wait = []
        self.queue_receiving = []
        self.queue_rereg: list[RRegPack] = []

    # -----------------------------
    def check_connect_to(self, node_id):
        for con in self.connect_list:
            if node_id == con.get_other_node(self.node_id).node_id:
                return True
        return False

    # -----------------------------
    def get_connect_to(self, node_id):
        for con in self.connect_list:
            if node_id == con.get_other_node(self.node_id).node_id:
                return con

    # -----------------------------
    def receive_tik(self):
        for cur_pack in self.queue_receiving:
            self._receive_pack(cur_pack)
        self.queue_receiving = []

    # -----------------------------
    def _receive_pack(self, cur_pack):
        cur_pack.size_was_sent = 0
        if cur_pack.type == "rreg":
            if self.check_connect_to(cur_pack.target_node_id):
                cur_pack.add_node(cur_pack.target_node_id)
                self._send_rrep(cur_pack)
            else:
                for rreg_pack in self.queue_rereg:
                    if cur_pack.target_node_id == rreg_pack.target_node_id:
                        self.queue_rereg.append(cur_pack)
                        return
                self.queue_rereg.append(cur_pack)
                for con in self.connect_list:
                    nn = con.get_other_node(self.node_id)
                    new_pack = deepcopy(cur_pack)
                    if new_pack.add_node(nn.node_id):
                        self.queue_to_send.append(new_pack)

        if cur_pack.type == "rrep":
            if cur_pack.path[0] == self.node_id:
                self._check_rrep(cur_pack)
            else:
                new_queue = []
                same_path = cur_pack.path[cur_pack.path.index(self.node_id) + 1 :]
                if self.node_id == 12:
                    print("Test")
                for rreg_pack in self.queue_rereg:
                    print(
                        f"package id: {cur_pack.current_node_id}, type: {cur_pack.type}"
                    )
                    if cur_pack.path[0] == rreg_pack.path[0]:
                        new_pack = deepcopy(cur_pack)
                        new_pack.path = rreg_pack.path + same_path
                        new_pack.set_current_node(self.node_id)
                        self.queue_to_send.append(new_pack)
                    else:
                        new_queue.append(rreg_pack)
                self.queue_rereg = new_queue

        if cur_pack.type == "data":
            if cur_pack.target_node_id == self.node_id:
                self.model_air.add_report(
                    cur_pack.path[0],
                    cur_pack.path[-1],
                    cur_pack.path[0],
                    self.model_air.get_current_time() - cur_pack.start_time,
                )

            else:
                self.queue_to_send.append(cur_pack)

    # -----------------------------
    def _send_rrep(self, rreg_pack):
        new_pack = adhoc_pack.RRepPack(rreg_pack.path)
        cur_con = self.get_connect_to(rreg_pack.target_node_id)
        new_pack.add_connect_inform(cur_con.get_quality_param())
        new_pack.set_current_node(self.node_id)
        cur_con = self.get_connect_to(new_pack.get_next_hop())
        new_pack.add_connect_inform(cur_con.get_quality_param())
        new_pack.start_time = rreg_pack.start_time
        self.queue_to_send.append(new_pack)

    # -----------------------------
    def _check_rrep(self, rrep_pack):
        new_queue = []
        for pack in self.queue_wait:
            if pack.target_node_id == rrep_pack.path[-1]:
                pack.path = rrep_pack.path
                self.queue_to_send.append(pack)
            else:
                new_queue.append(pack)
        self.queue_wait = new_queue

    # -----------------------------
    def send_message_to(self, target_node, data_size):
        #  create data pack
        cur_pack = adhoc_pack.DataPack(target_node_id=target_node, data_size=data_size)
        cur_pack.start_time = self.model_air.get_current_time()
        cur_pack.set_current_node(self.node_id)
        cur_pack.id = self.model_air.get_new_pack_id()
        #  check one hop connection
        if self.check_connect_to(target_node):
            self.queue_to_send.append(cur_pack)
            return

        # add pack to wait queue and wait until not  received RREP pack
        self.queue_wait.append(cur_pack)
        # send RREG pack to all hops
        for con in self.connect_list:
            cur_pack = adhoc_pack.RRegPack(
                source_node_id=self.node_id, target_node_id=target_node
            )
            nn = con.get_other_node(self.node_id)
            cur_pack.add_node(nn.node_id)
            cur_pack.start_time = self.model_air.get_current_time()
            self.queue_to_send.append(cur_pack)

    # -----------------------------
