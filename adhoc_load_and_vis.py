from adhoc_visualizer import DsrRouteVisualizer
from __init__ import _net_file_name, _ttl


ttl = _ttl
source_node_id = 2
destination_node_id = 38

if __name__ == "__main__":
    (DsrRouteVisualizer.from_xlsx(
        file_name=_net_file_name,
        ttl=ttl,
    )).animate_route_discovery(
    source_node_id=source_node_id,
    destination_node_id=destination_node_id,
    ttl=ttl,
)