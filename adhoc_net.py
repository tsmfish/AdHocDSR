import adhoc_nodes
import random
import cv2
import numpy
import openpyxl
import os

from adhoc_pack import RRegPack, DataPack


# ---------------------------------------------------------------------------------------------------------------
#  Class Ad hoc net
# --------------------------------------------------------------------------------------------------------------
class AdHocNet:
    def __init__(self):
        # base parameters   --------------------------------------------------
        self._plase_x_size = 1700
        self._plase_y_size = 500
        self._min_node_count = 30
        self._max_node_count = 50
        self._min_connect_count = 2
        self._max_connect_count = 5

        # main variable   --------------------------------------------------
        self.nodes_list = []
        self.connect_list = []
        self.system_time = 0
        self.id_counter = 1
        # Control variables  (variables for collecting statistics) --------------------------------------------------
        self.reports_list = []

        # debug variables   --------------------------------------------------
        self.debug_nodes_current_state_list = []

        # jamm parameters   --------------------------------------------------
        self.jamm_x = 700
        self.jamm_y = 500

    # ---------------------------------------------------------------------------------------------------------------
    def create_net(self):
        nodes_count = random.randint(self._min_node_count, self._max_node_count)
        for xx in range(nodes_count):
            new_node = adhoc_nodes.AdHocNode(
                node_id=xx,
                y=random.randint(0, self._plase_y_size),
                x=random.randint(0, self._plase_x_size),
                model_air=self,
            )
            new_node.__conection_count = random.randint(
                self._min_connect_count, self._max_connect_count
            )
            self.nodes_list.append(new_node)

        # -add connect--------------
        for xx in range(nodes_count):
            cur_node = self.nodes_list[xx]
            tmp_dist = [
                [
                    nn.node_id,
                    (
                        (nn.position_x - cur_node.position_x) ** 2
                        + (nn.position_y - cur_node.position_y) ** 2
                    )
                    ** 0.5,
                ]
                for nn in self.nodes_list
            ]
            tmp_dist.sort(key=lambda x: x[1])

            if len(cur_node.connect_list) < cur_node.__conection_count:
                for ind in range(1, len(tmp_dist)):
                    other_node = self.get_node_by_id(tmp_dist[ind][0])
                    if len(other_node.connect_list) < other_node.__conection_count:
                        if random.randint(0, 100) < 80:
                            new_connect = adhoc_nodes.AdHocConnect(cur_node, other_node)
                            cur_node.connect_list.append(new_connect)
                            other_node.connect_list.append(new_connect)
                            self.connect_list.append(new_connect)
                            if len(cur_node.connect_list) >= cur_node.__conection_count:
                                break

    # ---------------------------------------------------------------------------------------------------------------
    def get_current_time(self):
        return self.system_time

    # ---------------------------------------------------------------------------------------------------------------
    def get_new_pack_id(self):
        self.id_counter += 1
        return self.id_counter

    # ---------------------------------------------------------------------------------------------------------------
    def get_node_by_id(self, node_id):
        for node in self.nodes_list:
            if node.node_id == node_id:
                return node
        return None

    # ---------------------------------------------------------------------------------------------------------------
    def send_message(self, source_node, target_node, message_length):
        node = self.get_node_by_id(source_node)
        node.send_message_to(target_node, message_length)

    # ---------------------------------------------------------------------------------------------------------------
    def add_report(self, source_node, target_node, path, full_time):
        self.reports_list.append([source_node, target_node, path, full_time])

    # ---------------------------------------------------------------------------------------------------------------
    def show_net(self):
        output_image = numpy.zeros(
            [self._plase_y_size, self._plase_x_size, 3], dtype=numpy.uint8
        )
        # output jamm
        for x in range(1000, 100, -10):
            col_int = min(int(255 / ((x / 200) ** 2)), 255)
            cv2.circle(
                output_image, (self.jamm_x, self.jamm_y), x, (30, 0, col_int), -1
            )

        # output ad_hoc net
        for connect in self.connect_list:
            n1 = connect.nodes_pointers[0]
            n2 = connect.nodes_pointers[1]
            cv2.line(
                output_image,
                (n1.position_x, n1.position_y),
                (n2.position_x, n2.position_y),
                (120, 0, 0),
                2,
            )

        for node in self.nodes_list:
            cv2.circle(
                output_image, (node.position_x, node.position_y), 5, (0, 120, 0), 2
            )
            cv2.putText(
                output_image,
                str(node.node_id),
                (node.position_x - 2, node.position_y - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1,
                cv2.LINE_AA,
            )

        cv2.imshow("image", output_image)
        cv2.waitKey(0)

    # ---------------------------------------------------------------------------------------------------------------
    def collect_debug_information(self):
        self.debug_nodes_current_state_list.append([str(self.get_current_time())])
        rez = ["queue_to_send"]
        for node in self.nodes_list:
            state = ""
            # if node.node_id == 11:
            #     print("Test")
            for q in node.queue_to_send:
                if q is RRegPack or q is DataPack:
                    state = (
                        state
                        + q.type
                        + ": trgt-"
                        + str(q.target_node_id)
                        + ":"
                        + str(q.path)
                        + ";\n"
                    )
                else:
                    state = state + q.type + ":" + str(q.path) + ";\n"
            rez.append(state)
        self.debug_nodes_current_state_list.append(rez)

        rez = ["queue_wait"]
        for node in self.nodes_list:
            state = ""
            for q in node.queue_wait:
                state = state + str(q.get_next_hop()) + ";"
            rez.append(state)
        self.debug_nodes_current_state_list.append(rez)

    # ---------------------------------------------------------------------------------------------------------------
    def save_debug_information(self, file_name):
        wb = openpyxl.Workbook()
        curr_sheet = wb.worksheets[0]
        curr_sheet.title = "State"
        rez = ["nodes_id"]
        for node in self.nodes_list:
            rez.append(str(node.node_id))
        curr_sheet.append(rez)
        for dbg in self.debug_nodes_current_state_list:
            curr_sheet.append(dbg)

        wb.save(file_name)

    # ---------------------------------------------------------------------------------------------------------------
    def save_net_to_file(self, file_name):
        wb = openpyxl.Workbook()
        curr_sheet = wb.worksheets[0]
        curr_sheet.title = "Nodes"
        curr_sheet.append(["node_id", "position_y", "position_x"])
        for node in self.nodes_list:
            curr_sheet.append(
                [str(node.node_id), str(node.position_y), str(node.position_x)]
            )

        curr_sheet = wb.create_sheet("Connect")
        curr_sheet.append(
            [
                "first node",
                "second node",
                "default_bit_rate_error",
                "default_byte_per_tik",
            ]
        )
        for connect in self.connect_list:
            curr_sheet.append(
                [
                    str(connect.nodes_pointers[0].node_id),
                    str(connect.nodes_pointers[1].node_id),
                    str(connect.default_bit_rate_error),
                    str(connect.default_byte_per_tik),
                ]
            )
        wb.save(file_name)

    # ---------------------------------------------------------------------------------------------------------------
    def load_net_from_file(self, file_name):
        self.nodes_list = []
        self.connect_list = []
        self.system_time = 0
        self.id_counter = 1
        self.reports_list = []
        self.debug_nodes_current_state_list = []

        wb = openpyxl.load_workbook(file_name, data_only=True)
        # load nodes
        curr_sheet = wb["Nodes"]
        for row in range(2, curr_sheet.max_row + 1):
            new_node = adhoc_nodes.AdHocNode(
                node_id=int(curr_sheet.cell(row=row, column=1).value),
                y=int(curr_sheet.cell(row=row, column=2).value),
                x=int(curr_sheet.cell(row=row, column=3).value),
                model_air=self,
            )
            self.nodes_list.append(new_node)
        # load Connect
        curr_sheet = wb["Connect"]
        for row in range(2, curr_sheet.max_row + 1):
            n1 = int(curr_sheet.cell(row=row, column=1).value)
            n2 = int(curr_sheet.cell(row=row, column=2).value)
            cur_node = self.get_node_by_id(n1)
            other_node = self.get_node_by_id(n2)
            new_connect = adhoc_nodes.AdHocConnect(cur_node, other_node)
            new_connect.default_bit_rate_error = float(
                curr_sheet.cell(row=row, column=3).value
            )
            new_connect.default_byte_per_tik = float(
                curr_sheet.cell(row=row, column=4).value
            )
            cur_node.connect_list.append(new_connect)
            other_node.connect_list.append(new_connect)
            self.connect_list.append(new_connect)

    # ---------------------------------------------------------------------------------------------------------------
    def turn_one_tik(self):
        self.system_time += 1
        for connect in self.connect_list:
            connect.send_one_tik_part()

        # rez = ['queue_receiving']
        # for node in self.nodes_list:
        #     state = ''
        #     for q in node.queue_receiving:
        #         state = state + str(q.path)+';\n'
        #     rez.append(state)
        # self.debug_nodes_current_state_list.append(rez)

        for node in self.nodes_list:
            # if node.node_id == 11:
            #     print("Test")
            node.receive_tik()


# ---------------------------------------------------------------------------------------------------------------
#  Run collect statistic for compare DSR and NN
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    ad_hoc = AdHocNet()
    # ad_hoc.create_net()
    current_directory = os.getcwd()
    # ad_hoc.save_net_to_file(current_directory + r'\AdHoc_Net_test.xlsx')
    ad_hoc.load_net_from_file(file_name=current_directory + r"\AdHoc_Net_test.xlsx")
    ad_hoc.show_net()
    ad_hoc.send_message(source_node=31, target_node=23, message_length=100000)
    for i in range(200):
        ad_hoc.collect_debug_information()
        ad_hoc.turn_one_tik()

    ad_hoc.save_debug_information(file_name=current_directory + r"\debug.xlsx")
