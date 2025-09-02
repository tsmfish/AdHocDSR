import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Данные узлов и их связей из ранее предоставленной таблицы (фрагмент)
# Обновлено: добавлены новые связи согласно запросу
node_data = {
    'A001': ['A', ['A002', 'A003', 'B001', 'B003']],
    'A002': ['A', ['A001', 'A004', 'B002', 'B001', 'C001', 'C002']],
    'A003': ['A', ['A001', 'A005', 'A006', 'B001']], # A006 не в фрагменте
    'A004': ['A', ['A002', 'A007', 'B002', 'C001']], # A007 не в фрагменте
    'A005': ['A', ['A003', 'A008', 'B003', 'B001', 'B004', 'B005', 'C004']], # A008 не в фрагменте
    'B001': ['B', ['A001', 'A003', 'B002', 'C001', 'A002', 'B003', 'A005']],
    'B002': ['B', ['A002', 'A004', 'B001', 'B003', 'C002']],
    'B003': ['B', ['A005', 'B002', 'B004', 'C003', 'A001', 'B001']],
    'B004': ['B', ['B003', 'B005', 'C003', 'A005']],
    'B005': ['B', ['B004', 'C004', 'C005', 'A005']],
    'C001': ['C', ['B001', 'C002', 'C006', 'A002', 'A004']], # C006 не в фрагменте
    'C002': ['C', ['B002', 'C001', 'C003', 'C007', 'A002']], # C007 не в фрагменте
    'C003': ['C', ['B003', 'B004', 'C002', 'C008']], # C008 не в фрагменте
    'C004': ['C', ['B005', 'C005', 'C009', 'A005']], # C009 не в фрагменте
    'C005': ['C', ['B005', 'C004', 'C010']], # C010 не в фрагменте
}

# Отфильтруем связи, чтобы включать только узлы, которые фактически присутствуют в node_data
valid_node_ids = set(node_data.keys())
cleaned_node_data = {}
for node_id, attributes in node_data.items():
    level = attributes[0]
    neighbors = [n for n in attributes[1] if n in valid_node_ids]
    cleaned_node_data[node_id] = [level, neighbors]

# Создаем пустой граф
G = nx.Graph()

# Добавляем узлы и их атрибуты (уровень)
for node_id, attributes in cleaned_node_data.items():
    level = attributes[0]
    G.add_node(node_id, level=level)

# Добавляем ребра (связи)
for node_id, attributes in cleaned_node_data.items():
    neighbors = attributes[1]
    for neighbor_id in neighbors:
        G.add_edge(node_id, neighbor_id)

# Определяем цвета для разных уровней
level_colors = {
    'A': '#FF6B6B',  # Красный (Energetic Red) - для переднего края
    'B': '#F7B731',  # Желтый (Bright Yellow) - для среднего эшелона
    'C': '#4ECDC4'   # Бирюзовый (Playful Teal) - для тылового эшелона
}

# Получаем цвета для каждого узла
node_colors = [level_colors[G.nodes[node]['level']] for node in G.nodes()]

plt.figure(figsize=(14, 10)) # Увеличим размер фигуры для лучшей читаемости

# Используем spring_layout для компоновки узлов
pos = nx.spring_layout(G, k=0.4, iterations=50, seed=42)

# --- Добавление имитации РЭБ ---

# Определяем позиции средств РЭБ противника
# Увеличиваем радиус и корректируем позицию, чтобы накрывать узлы A и частично B
ew_sources = {
    'EW1': {'pos': np.array([-0.3, 0.7]), 'range': 1.1, 'angle': 0}, # Позиция, радиус, угол для эллипса
    'EW2': {'pos': np.array([0.7, 0.7]), 'range': 1.1, 'angle': 0}
}

# Базовое SNR для всех узлов
base_snr = 30 # dB

# Функция для расчета SNR с учетом влияния РЭБ
def calculate_snr_with_ew_effect(node_pos, ew_sources, base_snr=30, min_snr=0):
    current_snr = base_snr
    for ew_id, ew_info in ew_sources.items():
        ew_pos = ew_info['pos']
        ew_range = ew_info['range']
        
        distance = np.linalg.norm(node_pos - ew_pos)
        
        if distance < ew_range:
            normalized_distance = distance / ew_range
            
            max_possible_reduction = base_snr - min_snr
            
            # Случайное снижение, где нижняя граница выше, когда ближе к источнику
            # и верхняя граница также пропорциональна близости
            lower_bound_reduction = (1 - normalized_distance) * max_possible_reduction * 0.7
            upper_bound_reduction = (1 - normalized_distance) * max_possible_reduction * 1.0
            
            snr_reduction = np.random.uniform(lower_bound_reduction, upper_bound_reduction)
            
            current_snr = max(min_snr, current_snr - snr_reduction)
    return current_snr

# Назначаем базовое SNR и рассчитываем SNR с учетом РЭБ для каждого узла
node_snrs = {}
for node_id, node_pos in pos.items():
    node_snrs[node_id] = calculate_snr_with_ew_effect(node_pos, ew_sources, base_snr=base_snr, min_snr=0)
    G.nodes[node_id]['snr'] = node_snrs[node_id]


# Отрисовка графа
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, alpha=0.9)

# Подписи узлов (черным шрифтом, по центру кружка)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_color='black', verticalalignment='center') 

nx.draw_networkx_edges(G, pos, edge_color='#607D8B', width=1.5, alpha=0.7)

# Рисуем зоны РЭБ
ax = plt.gca()
for ew_id, ew_info in ew_sources.items():
    ew_pos = ew_info['pos']
    ew_range = ew_info['range']
    ew_angle = ew_info['angle']
    
    ew_patch = plt.matplotlib.patches.Ellipse(
        ew_pos,
        ew_range * 2,       # Ширина эллипса
        ew_range * 1.5,     # Высота эллипса (сделаем его немного вытянутым)
        angle=ew_angle,     # Угол поворота эллипса
        color='red',
        alpha=0.15,         # Полупрозрачный
        label=f'Зона РЕБ ({ew_id})'
    )
    ax.add_patch(ew_patch)

# Добавляем подписи SNR к узлам с отступом вниз
snr_labels_pos = {node_id: (p[0], p[1] - 0.08) for node_id, p in pos.items()} # Смещаем по Y вниз
snr_labels = {node_id: f'{node_snrs[node_id]:.1f} дБ' for node_id in G.nodes()}
nx.draw_networkx_labels(G, snr_labels_pos, labels=snr_labels, font_size=8, font_color='black', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))


plt.title("Графова модель Mesh-мережі з імітацією впливу РЕБ", size=16, color='#374151')
plt.axis('off')
plt.legend(loc='lower left', bbox_to_anchor=(0, 0))
plt.show()
