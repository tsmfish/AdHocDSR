import random
from copy import deepcopy, copy
from adhoc_pack import RReqPack, BasePack, DataPack, RRepPack
from bandwidth.wi_fi import calculate_speed_degradation


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
        self.default_byte_per_tik = 3000
        self.current_byte_per_tik = 3000
        self.sent_byte_in_current_tic = 0
        # self.sent_byte_in_current_tic_to_back = 0
        # jamm parameters   -------------------------------------------------
        self.signal_value = 80.0  # mkwat
        self.noice_value = 2.0  # mkwat
        # self.error_probability = 2.0  #


    # ---------------------------------------------------------------------------------------------------------------
    def get_nodes(self):
        return self.nodes_pointers[0], self.nodes_pointers[1]

    # ---------------------------------------------------------------------------------------------------------------
    def get_quality_param(self):
        return self.snr

    # ---------------------------------------------------------------------------------------------------------------
    def calculate_error_probability(self):
        distance =(((self.nodes_pointers[0].position_x- self.nodes_pointers[1].position_x)**2) +
                   ((self.nodes_pointers[0].position_y - self.nodes_pointers[1].position_y) ** 2)
                   ) ** 0.5
        th_adjust = 300
        if distance > th_adjust:
            signal_value = self.signal_value * (1/((distance/th_adjust)**2))
        else:
            signal_value = self.signal_value
        # signal_value = self.signal_value
        adjust_factor = calculate_speed_degradation( signal_value / self.noice_value)
        self.current_byte_per_tik = int(self.default_byte_per_tik * adjust_factor)


        # if self.signal_value > self.noice_value:
        #     adjust_factor = calculate_speed_degradation(snr)
        # else:
        #     adjust_factor = 0
        #
        #
        # snr = self.signal_value / self.noice_value

        # if snr > 7:
        #     self.current_byte_per_tik = self.default_byte_per_tik
        # elif snr > 5:
        #     self.current_byte_per_tik = self.default_byte_per_tik * 0.9
        # elif snr > 4:
        #     self.current_byte_per_tik = self.default_byte_per_tik * 0.8
        # elif snr > 3:
        #     self.current_byte_per_tik = self.default_byte_per_tik * 0.5
        # elif snr > 2:
        #     self.current_byte_per_tik = self.default_byte_per_tik * 0.3
        # else:
        #     self.current_byte_per_tik = self.default_byte_per_tik * 0.1


        return

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

        for pack in source_node.queue_to_send:
            if pack.get_next_hop() == target_node.node_id:
                # if source_node.node_id == 7 and pack.type ==  "rrep":
                #     print("TTest")
                # if pack.type == "data":
                #     print("connect Test")

                pack.size_was_sent = self._try_to_send_pack(pack)
                if pack.size_was_sent >= pack.get_size():
                    target_node.queue_receiving.append(pack)
                    continue
            delay_time = (
                source_node.model_air.get_current_time()
                - pack.time_receive_in_current_node
            )
            if 100 < delay_time:
                # if pack.type == "data":
                #     print("connect TTest")
                source_node.model_air.add_lost(
                    source_node=pack.path[0],
                    target_node=pack.destination_node_id,
                    path=str(pack.path),
                    break_node=str(source_node.node_id)
                    + ":"
                    + str(pack.get_next_hop()),
                    pack_type=pack.type,
                )
                # if pack.type ==  "data":
                #     print("TTest connect")

                continue
            non_send_pack.append(pack)

        source_node.queue_to_send = non_send_pack
        self.sent_byte_in_current_tic = 0

    # ---------------------------------------------------------------------------------------------------------------
    def _try_to_send_pack(self, pack):
        size = pack.get_size()
        part_size = 10
        total_send = pack.size_was_sent
        if size - total_send < part_size:
            part_size = size - total_send

        while (
            self.current_byte_per_tik > self.sent_byte_in_current_tic + part_size
        ) and total_send < size:
            self.sent_byte_in_current_tic += part_size
            total_send += part_size
            # if not self._check_error(size):
            #     total_send += part_size
            if size - total_send < part_size:
                part_size = size - total_send
        return total_send

    # ---------------------------------------------------------------------------------------------------------------
    # def _check_error(self, size):
    #     if random.randint(0, 500) < self._jamm_threshold:
    #         return True
    #     return False

    # ---------------------------------------------------------------------------------------------------------------
    # def send_pack(self, pack_length_in_byte):
    #     return self._use_snr(pack_length_in_byte)

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
    # def _use_snr(self, pack_length_in_byte):
    #     threshold = 10000 * (
    #         (1 - (1 / (1 + 2.71818281828 ** (-self.snr)))) ** 2
    #     ) + random.randint(1, 4)
    #     for xx in range(0, pack_length_in_byte, 100):
    #         if threshold > random.randint(0, 10000):
    #             return False
    #     return True

    # ----------------------------------------------
    def get_other_node(self, my_id: int):
        if my_id == self.nodes_pointers[0].node_id:
            return self.nodes_pointers[1]
        return self.nodes_pointers[0]


# ---------------------------------------------------------------------------------------------------------------
#  Class  ad_hoc node
# --------------------------------------------------------------------------------------------------------------
class AdHocNode:
    def __init__(self, node_id: int, y, x, model_air):
        self.node_id: int = node_id
        self.position_x = x
        self.position_y = y
        self.connect_list = []
        self.flag_work = True
        self.__conection_count = 3
        self.model_air = model_air
        self.queue_to_send = []
        self.queue_wait = []
        self.queue_receiving = []
        self.queue_rereg: list[RReqPack] = []
        self.wait_rrep = 40 # tic after received first rrep
        # -- # variables for test only--------

    # -----------------------------
    def check_connect_to(self, node_id: int):
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
        self._check_data_send()

    def _add_to_queue_to_send(self, cur_pack):
        cur_pack.set_current_node(self.node_id)
        cur_pack.time_receive_in_current_node = self.model_air.get_current_time()
        self.queue_to_send.append(cur_pack)

    # -----------------------------
    def _receive_pack(self, cur_pack: BasePack):
        cur_pack.size_was_sent = 0
        if isinstance(cur_pack, RReqPack):
            if self.check_connect_to(cur_pack.destination_node_id):
                cur_pack.add_node(cur_pack.destination_node_id)
                self._send_rrep(cur_pack)
            else:
                if cur_pack.ttl > 0:  # check TTL before transit packet
                    cur_pack.ttl = cur_pack.ttl - 1

                    for rreq_pack in self.queue_rereg:
                        if (
                            cur_pack.destination_node_id
                            == rreq_pack.destination_node_id
                        ):
                            self.queue_rereg.append(cur_pack)
                            return
                    self.queue_rereg.append(cur_pack)
                    for con in self.connect_list:
                        nn = con.get_other_node(self.node_id)
                        new_pack = deepcopy(cur_pack)
                        if new_pack.add_node(nn.node_id):
                            self._add_to_queue_to_send(new_pack)

        if isinstance(cur_pack, RRepPack):
            if cur_pack.path[0] == self.node_id:
                self._check_rrep(cur_pack)
            else:
                same_path = cur_pack.path[cur_pack.path.index(self.node_id) + 1 :]
                # if self.node_id == 28:
                #     print("Test")
                for rreq_pack in self.queue_rereg:
                    if cur_pack.path[0] == rreq_pack.path[0]:
                        fl_add = True
                        for pp in same_path:
                            if pp in rreq_pack.path:
                                fl_add = False

                        if fl_add:
                            new_pack = deepcopy(cur_pack)
                            new_pack.path = rreq_pack.path + same_path
                            new_pack.set_current_node(self.node_id)
                            if len (new_pack.path) < 20:
                                self._add_to_queue_to_send(new_pack)

        new_queue = []
        for rreq_pack in self.queue_rereg:
            if rreq_pack.start_time + 50 > self.model_air.get_current_time():
                new_queue.append(rreq_pack)
        self.queue_rereg = new_queue

        if isinstance(cur_pack, DataPack):
            if cur_pack.destination_node_id == self.node_id:
                if cur_pack.add_information is not None:
                    self.model_air.add_report(
                        source_node=cur_pack.path[0],
                        target_node=cur_pack.path[-1],
                        path=cur_pack.path,
                        full_time=self.model_air.get_current_time()
                        - cur_pack.start_time,pack_size=cur_pack.get_size()
                    )
            else:
                if cur_pack.ttl > 0:
                    cur_pack.ttl = cur_pack.ttl - 1
                    cur_pack.set_current_node(self.node_id)
                    self._add_to_queue_to_send(cur_pack)

    # -----------------------------
    def _send_rrep(self, rreq_pack: RReqPack):
        new_pack = RRepPack(rreq_pack.path)
        cur_con = self.get_connect_to(rreq_pack.destination_node_id)
        new_pack.add_connect_inform(cur_con.get_quality_param())
        new_pack.set_current_node(self.node_id)
        cur_con = self.get_connect_to(new_pack.get_next_hop())
        new_pack.add_connect_inform(cur_con.get_quality_param())
        new_pack.start_time = rreq_pack.start_time
        self._add_to_queue_to_send(new_pack)

    # -----------------------------
    def _check_rrep(self, rrep_pack):
        for pack in self.queue_wait:
            if pack.destination_node_id == rrep_pack.destination_node_id:
                rrep_pack.start_time = self.model_air.get_current_time()
                pack.rrep_list.append(rrep_pack)

    # # -----------------------------
    # def _select_best_path(self, rrep_list:list[Any]):

    # -----------------------------
    def _check_data_send(self):
        new_queue = []
        for pack in self.queue_wait:
            if len(pack.rrep_list) > 0:
                all_time = [rrep.start_time for rrep in pack.rrep_list]
                if self.model_air.get_current_time() > (min(all_time) + self.wait_rrep):
                    for rrep in pack.rrep_list:
                        test_pack = copy(pack)
                        test_pack.path = rrep.path
                        test_pack.add_information = rrep.add_information
                        test_pack.metrics = {"simple metric": 0}
                        self.model_air.add_data_pack_for_investigation(test_pack)
                    continue
            new_queue.append(pack)
        self.queue_wait = new_queue

    # -----------------------------
    def send_message_to(self, destination_node_id: int, data_size: int):
        #  create data pack
        cur_pack = DataPack(
            source_node_id=self.node_id,
            destination_node_id=destination_node_id,
            data_size=data_size,
        )
        cur_pack.start_time = self.model_air.get_current_time()
        cur_pack.set_current_node(self.node_id)
        cur_pack.id = self.model_air.get_new_pack_id()
        #  check one hop connection
        if self.check_connect_to(destination_node_id):
            self._add_to_queue_to_send(cur_pack)
            return

        # add pack to wait queue and wait until not  received RREP pack
        self.queue_wait.append(cur_pack)
        # send RREG pack to all hops
        for con in self.connect_list:
            cur_pack = RReqPack(
                source_node_id=self.node_id, destination_node_id=destination_node_id
            )
            nn = con.get_other_node(self.node_id)
            cur_pack.add_node(nn.node_id)
            cur_pack.start_time = self.model_air.get_current_time()
            self._add_to_queue_to_send(cur_pack)

    # -----------------------------
