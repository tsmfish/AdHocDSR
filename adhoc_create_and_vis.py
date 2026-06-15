from adhoc_net import AdHocNet
from adhoc_visualizer import DsrRouteVisualizer


ad_hoc = AdHocNet(ttl=8)
ad_hoc.create_net()

source_node_id = 1
destination_node_id = 25

if __name__ == "__main__":
    (DsrRouteVisualizer.from_adhoc_net(ad_hoc)
    .animate_route_discovery(
        source_node_id=source_node_id,
        destination_node_id=destination_node_id,
        ttl=8,
    ))