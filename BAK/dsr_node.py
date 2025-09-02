import random
import csv
import DSR_NN
# ---------------------------------------------------------------------------------------------------------------
#  Class connection
# ---------------------------------------------------------------------------------------------------------------
class Connect():
    def __init__(self):
        self.nodes_id= [0, 0]
        self.bit_rate_error = 0.01
        self.snr = 2
        self.flag_work = True

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
        threshold = 10000*((1- (1/ (1+ 2.71818281828**(-self.snr))))**2) + random.randint(1, 4)
        for xx in range(0, pack_length_in_byte, 100):
            if threshold > random.randint(0, 10000):
                return False
        return True


    def get_other_node(self, my_id):
        if my_id == self.nodes_id[0]:
          return self.nodes_id[1]
        return self.nodes_id[0]


# ---------------------------------------------------------------------------------------------------------------
#  Class node
# --------------------------------------------------------------------------------------------------------------
class DSR_node():
    def __init__(self, id):
        self.node_id= id
        self.connect_list = []
        self.flag_work = True

    # -----------------------------
    def check_connect_to(self, id):
        for con in self.connect_list:
            if id in con.nodes_id:
                return self.flag_work
        return False

    # -----------------------------
    def get_connect_to(self, id):
        for con in self.connect_list:
            if id in con.nodes_id:
                return con

    # -----------------------------
    def send_rreg(self, node_list, target_node):
        rez = []
        final = []
        for con in self.connect_list:
            nn = con.get_other_node(self.node_id)
            if nn not in node_list:
                new_rreg = node_list[:]
                new_rreg.append(nn)
                if nn == target_node:
                    final.append(new_rreg)
                else:
                    rez.append(new_rreg)

        return rez, final


# ---------------------------------------------------------------------------------------------------------------
#  Class net
# --------------------------------------------------------------------------------------------------------------
class nets_mesh():
    def __init__(self):
        self.nodes_list= []
        self.connect_list = []
        self.nn_data = []
        self.nn = None
        self._min_node_count = 15
        self._max_node_count = 30
        self._min_connect_count = 1
        self._max_connect_count = 3
        self._neighborhood = 5


    # ---------------------------------------------------------------------------------------------------------------
    def load_nn(self, nn_file_name):
        self.nn = DSR_NN.Run_NN(nn_file_name)

    # ---------------------------------------------------------------------------------------------------------------
    def create_net(self):
        nodes_count = random.randint(self._min_node_count, self._max_node_count)
        for xx in range(nodes_count):
            new_node = DSR_node(xx)
            self.nodes_list.append(new_node)
        # -add connect--------------
        for xx in range(nodes_count):
            con_count = random.randint(self._min_connect_count, self._max_connect_count)
            loop_calc = 0
            while len(self.nodes_list[xx].connect_list)  < con_count and loop_calc < 30:
                min_n = max(xx -self._neighborhood, 0 )
                max_n = min(xx + self._neighborhood, nodes_count-1)
                con_nod = random.randint(min_n, max_n)
                loop_calc += 1
                if con_nod != xx and (not self.nodes_list[con_nod].check_connect_to(xx)):
                    if len(self.nodes_list[con_nod].connect_list) >= self._max_connect_count:
                        continue
                    new_con = Connect()
                    new_con.nodes_id=[xx, con_nod]
                    self.nodes_list[con_nod].connect_list.append(new_con)
                    self.nodes_list[xx].connect_list.append(new_con)
                    self.connect_list.append(new_con)


    # ---------------------------------------------------------------------------------------------------------------
    def impact_REB(self):
        for con in self.connect_list:
            con.bit_rate_error = (random.randint(20, 100))/10000.0
            con.snr = (random.randint(30, 130))/10.0

    # ---------------------------------------------------------------------------------------------------------------
    def create_path(self, from_node, to_node):
        rreg = [[from_node]]
        final = []
        while len(rreg) > 0:
            cur_rreg = rreg[0]
            rreg = rreg[1:]
            if len(cur_rreg) < len(self.nodes_list)//2:
                cur_rreg, final_rreg = self.nodes_list[cur_rreg[-1]].send_rreg(cur_rreg, to_node)
                final = final + final_rreg
                rreg = rreg + cur_rreg
        return final

    # ---------------------------------------------------------------------------------------------------------------
    def send_pack(self, path, pack_length, loop = 1000):
        rez = 0
        for xx in range(loop):
            for pp in range(len(path)-1):
                con = self.nodes_list[path[pp]].get_connect_to(path[pp + 1])
                if not con.send_pack(pack_length ):
                    rez += 1
                    break
        return float(rez )/ loop

    # -----------------------------
    def create_histogram(self, path_list):
        hh = [0]*10
        for pp in range(len(path_list) - 1):
            con = self.nodes_list[path_list[pp]].get_connect_to(path_list[pp + 1])
            # val = int(con.bit_rate_error * 1000)
            val = int(con.snr) - 3
            if val > len(hh)-1:
                val = len(hh)-1
            if val < 0:
                val = 0
            hh[val] += 1
        return hh

    # -----------------------------
    def create_data_to_nn(self):
        path = self.create_path(from_node=3, to_node=len(self.nodes_list) - 3)
        for pack_size in [300 , 500, 700,1000,1200, 1500] :
            for pp in path:
                row = [str(self.send_pack(pp, pack_size)), str(len(pp)), str(pack_size)]
                row = row + self.create_histogram(pp)
                self.nn_data.append(row)
        return self.nn_data

    # -----------------------------
    def save_file_to_disc(self, file_name):
        f = open(file_name, 'a+', newline='\n')
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        for student_row in self.nn_data:
            wr.writerow(student_row)
        f.close()

    # -----------------------------
    def save_compare_results(self, file_name):
        path = self.create_path(from_node=3, to_node=len(self.nodes_list) - 3)
        for pack_size in [300 , 500, 700,1000,1200, 1500] :
            true_target = []
            input_rows = []
            for pp in path:
                true_target.append(self.send_pack(pp, pack_size))
                row = [len(pp), pack_size] + self.create_histogram(pp)
                input_rows.append(row)
            if len(input_rows) == 0:
                continue
            pred = self.nn.run(input_rows)
            pred = [x[0]/3 for x in pred]
            forecast_index = pred.index(min(pred))
            dsr_path = [x[0] for x in  input_rows ]
            dsr_index = dsr_path.index(min(dsr_path))

            target_index = true_target.index(min(true_target))
            row = [len(self.nodes_list), len(self.connect_list), pack_size,target_index, dsr_index, forecast_index,
                   len(path[target_index]),len(path[dsr_index]),len(path[forecast_index]),true_target[target_index],
                   true_target[dsr_index], true_target[forecast_index], pred[forecast_index]]
            f = open(file_name, 'a+', newline='\n')
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(row)



# ---------------------------------------------------------------------------------------------------------------
#  Run collect statistic for compare DSR and NN
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    for xx in range(200):
        cur_net = nets_mesh()
        cur_net.create_net()
        cur_net.impact_REB()
        cur_net = nets_mesh()
        cur_net.create_net()
        cur_net.impact_REB()
        cur_net.load_nn(r'd:\Sychov\HNUPS\Projects\DSR_data\dsr_snr_net_v2_Best.hdf5')
        cur_net.save_compare_results(r'd:\Sychov\HNUPS\Projects\DSR_data\rez\snr_rez_full_v2.csv')


    # for xx in range(30):
    #     cur_net = nets_mesh()
    #     cur_net.create_net()
    #     cur_net.impact_REB()
    #
    #
    #     cur_net.create_data_to_nn()
    #     cur_net.save_file_to_disc( file_name= r'd:\Sychov\HNUPS\Projects\DSR_data\nn_data.csv')




    # path = cur_net.create_path(from_node=3, to_node=len(cur_net.nodes_list) - 3)
    # rez = []
    # for pp in path:
    #     rez.append({'ймовірність втрати пакету':cur_net.send_pack( pp, 300), 'шлях':pp})


    # G = nx.Graph()
    #
    # for node in cur_net.nodes_list:
    #     G.add_node(node.node_id, level=0)
    # for con in cur_net.connect_list:
    #     G.add_edge(con.nodes_id[0],con.nodes_id[1], label=str(int(1000 * con.bit_rate_error)))
    #
    # pos = nx.spring_layout(G, k=0.4, iterations=50, seed=42)
    # # Отрисовка графа
    # nx.draw_networkx_nodes(G, pos, node_color='#FF6B6B', node_size=1200, alpha=0.9)
    #
    # # Подписи узлов (черным шрифтом, по центру кружка)
    # nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_color='black', verticalalignment='center')
    #
    # nx.draw_networkx_edges(G, pos, edge_color='#607D8B', width=1.5, alpha=0.7)
    # edge_labels = {(u, v): G[u][v]['label'] for u, v in G.edges()}
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12, font_color='red')
    #
    # plt.title("Графова модель Mesh-мережі з імітацією впливу РЕБ", size=16, color='#374151')
    # plt.axis('off')
    # # plt.legend(loc='lower left', bbox_to_anchor=(0, 0))
    # plt.show()
    print('test')





