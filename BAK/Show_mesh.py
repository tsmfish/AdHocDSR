import dsr_node
import networkx as nx
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------------------------------------------
#  Show net as graph
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":


    cur_net = dsr_node.nets_mesh()
    cur_net.create_net()
    cur_net.impact_REB()





    # path = cur_net.create_path(from_node=3, to_node=len(cur_net.nodes_list) - 3)
    # rez = []
    # for pp in path:
    #     rez.append({'ймовірність втрати пакету':cur_net.send_pack( pp, 300), 'шлях':pp})


    G = nx.Graph()

    for node in cur_net.nodes_list:
        G.add_node(node.node_id, level=0)
    for con in cur_net.connect_list:
        G.add_edge(con.nodes_id[0],con.nodes_id[1], label=str(int(1000 * con.bit_rate_error)))

    pos = nx.spring_layout(G, k=0.4, iterations=50, seed=42)
    # Отрисовка графа
    nx.draw_networkx_nodes(G, pos, node_color='#FF6B6B', node_size=1200, alpha=0.9)

    # Подписи узлов (черным шрифтом, по центру кружка)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_color='black', verticalalignment='center')

    nx.draw_networkx_edges(G, pos, edge_color='#607D8B', width=1.5, alpha=0.7)
    edge_labels = {(u, v): G[u][v]['label'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12, font_color='red')

    plt.title("Графова модель Mesh-мережі з імітацією впливу РЕБ", size=16, color='#374151')
    plt.axis('off')
    # plt.legend(loc='lower left', bbox_to_anchor=(0, 0))
    plt.show()
    print('test')