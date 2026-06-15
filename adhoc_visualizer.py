"""
Standalone visualization module for Ad-Hoc DSR-like packet propagation.

Features:
- Does not modify the main simulation logic.
- Visualizes smooth RREQ/RREP packet movement over network edges.
- Controls TTL.
- Shows packet delivery failures.
- Can work with an existing AdHocNet object.
- Can optionally load a topology from an .xlsx file through AdHocNet.

Packet types:
- RREQ: route request, flooded through the network.
- RREP: route reply, returned through discovered path.

Example:
    from adhoc_net import AdHocNet
    from adhoc_visualizer import DsrRouteVisualizer

    net = AdHocNet(ttl=8)
    net.create_net()

    visualizer = DsrRouteVisualizer.from_adhoc_net(net)
    visualizer.animate_route_discovery(
        source_node_id=1,
        destination_node_id=25,
        ttl=8,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, TextBox


class VisualPacketType(str, Enum):
    RREQ = "RREQ"
    RREP = "RREP"


class VisualPacketStatus(str, Enum):
    MOVING = "moving"
    DELIVERED = "delivered"
    DROPPED = "dropped"


@dataclass(frozen=True)
class VisualNode:
    node_id: int
    x: float
    y: float


@dataclass(frozen=True)
class VisualEdge:
    first_node_id: int
    second_node_id: int


@dataclass
class VisualPacket:
    packet_id: int
    packet_type: VisualPacketType
    source_node_id: int
    destination_node_id: int
    current_from_node_id: int
    current_to_node_id: int
    path: list[int]
    ttl: int
    progress: float = 0.0
    status: VisualPacketStatus = VisualPacketStatus.MOVING
    drop_reason: str = ""

    def clone_for_next_hop(
        self,
        packet_id: int,
        from_node_id: int,
        to_node_id: int,
        ttl: int,
        path: list[int],
    ) -> "VisualPacket":
        return VisualPacket(
            packet_id=packet_id,
            packet_type=self.packet_type,
            source_node_id=self.source_node_id,
            destination_node_id=self.destination_node_id,
            current_from_node_id=from_node_id,
            current_to_node_id=to_node_id,
            path=path,
            ttl=ttl,
        )


@dataclass
class VisualEvent:
    time_step: int
    message: str
    packet_type: VisualPacketType | None = None
    path: list[int] = field(default_factory=list)


class DsrRouteVisualizer:
    def __init__(
        self,
        nodes: list[VisualNode],
        edges: list[VisualEdge],
        place_x_size: int = 1700,
        place_y_size: int = 500,
    ):
        self.nodes: dict[int, VisualNode] = {node.node_id: node for node in nodes}
        self.edges = edges
        self.place_x_size = place_x_size
        self.place_y_size = place_y_size

        self.neighbors: dict[int, set[int]] = {node_id: set() for node_id in self.nodes}
        for edge in edges:
            self.neighbors.setdefault(edge.first_node_id, set()).add(edge.second_node_id)
            self.neighbors.setdefault(edge.second_node_id, set()).add(edge.first_node_id)

        self.packet_speed = 0.08
        self.packet_id_counter = 0
        self.current_time_step = 0

        self.active_packets: list[VisualPacket] = []
        self.delivered_rreq_paths: list[list[int]] = []
        self.delivered_rrep_paths: list[list[int]] = []
        self.dropped_packets: list[VisualPacket] = []
        self.events: list[VisualEvent] = []
        self.send_rrep_packs: dict[int, list[int]] = {}

        self.source_node_id: int | None = None
        self.destination_node_id: int | None = None
        self.initial_ttl = 0
        self.route_found = False
        self.route_discovery_finished = False

        self.is_paused = False
        self.step_requested = False
        self.animation: FuncAnimation | None = None
        self.figure: Any = None
        self.axis: Any = None
        self.ttl_text_box: TextBox | None = None

    @classmethod
    def from_adhoc_net(cls, ad_hoc_net: Any) -> "DsrRouteVisualizer":
        nodes = [
            VisualNode(
                node_id=node.node_id,
                x=node.position_x,
                y=node.position_y,
            )
            for node in ad_hoc_net.nodes_list
        ]

        edges = [
            VisualEdge(
                first_node_id=connect.nodes_pointers[0].node_id,
                second_node_id=connect.nodes_pointers[1].node_id,
            )
            for connect in ad_hoc_net.connect_list
        ]

        return cls(
            nodes=nodes,
            edges=edges,
            place_x_size=ad_hoc_net._plase_x_size,
            place_y_size=ad_hoc_net._plase_y_size,
        )

    @classmethod
    def from_xlsx(cls, file_name: str, ttl: int = 18) -> "DsrRouteVisualizer":
        from adhoc_net import AdHocNet

        ad_hoc_net = AdHocNet(ttl=ttl)
        ad_hoc_net.load_net_from_file(file_name)
        return cls.from_adhoc_net(ad_hoc_net)

    def animate_route_discovery(
        self,
        source_node_id: int,
        destination_node_id: int,
        ttl: int = 18,
        interval_ms: int = 40,
        packet_speed: float = 0.08,
        max_frames: int = 2000,
        show_node_ids: bool = True,
        save_to: str | None = None,
    ) -> None:
        if source_node_id not in self.nodes:
            raise ValueError(f"Unknown source node id: {source_node_id}")

        if destination_node_id not in self.nodes:
            raise ValueError(f"Unknown destination node id: {destination_node_id}")

        self.source_node_id = source_node_id
        self.destination_node_id = destination_node_id
        self.initial_ttl = ttl
        self.packet_speed = packet_speed

        self._reset_state()
        self._start_rreq(source_node_id, destination_node_id, ttl)

        self.figure, self.axis = plt.subplots(figsize=(14, 7))
        self.figure.canvas.manager.set_window_title("DSR Route Discovery Visualization")
        plt.subplots_adjust(bottom=0.18)

        self._create_controls()

        def update(frame_index: int) -> list[Any]:
            if self.is_paused and not self.step_requested:
                self._draw(self.axis, show_node_ids=show_node_ids)
                return []

            self.step_requested = False

            if not self.route_discovery_finished:
                self._simulation_step()

            self._draw(self.axis, show_node_ids=show_node_ids)

            return []

        self.animation = FuncAnimation(
            self.figure,
            update,
            frames=max_frames,
            interval=interval_ms,
            blit=False,
            repeat=False,
        )

        if save_to:
            self.animation.save(save_to)

        plt.show()

    def _create_controls(self) -> None:
        pause_axis = plt.axes([0.08, 0.04, 0.10, 0.05])
        resume_axis = plt.axes([0.20, 0.04, 0.10, 0.05])
        step_axis = plt.axes([0.32, 0.04, 0.10, 0.05])
        restart_axis = plt.axes([0.44, 0.04, 0.10, 0.05])
        ttl_axis = plt.axes([0.62, 0.04, 0.10, 0.05])
        apply_ttl_axis = plt.axes([0.74, 0.04, 0.14, 0.05])

        pause_button = Button(pause_axis, "Pause")
        resume_button = Button(resume_axis, "Resume")
        step_button = Button(step_axis, "Step")
        restart_button = Button(restart_axis, "Restart")
        self.ttl_text_box = TextBox(ttl_axis, "TTL ", initial=str(self.initial_ttl))
        apply_ttl_button = Button(apply_ttl_axis, "Apply TTL")

        pause_button.on_clicked(self._on_pause_clicked)
        resume_button.on_clicked(self._on_resume_clicked)
        step_button.on_clicked(self._on_step_clicked)
        restart_button.on_clicked(self._on_restart_clicked)
        apply_ttl_button.on_clicked(self._on_apply_ttl_clicked)

        self._control_widgets = [
            pause_button,
            resume_button,
            step_button,
            restart_button,
            self.ttl_text_box,
            apply_ttl_button,
        ]

    def _on_pause_clicked(self, event: Any) -> None:
        self.is_paused = True
        self._add_event("Visualization paused")

    def _on_resume_clicked(self, event: Any) -> None:
        self.is_paused = False
        self._add_event("Visualization resumed")

    def _on_step_clicked(self, event: Any) -> None:
        self.is_paused = True
        self.step_requested = True
        self._add_event("Manual step")

    def _on_restart_clicked(self, event: Any) -> None:
        self._restart_with_current_ttl()

    def _on_apply_ttl_clicked(self, event: Any) -> None:
        if self.ttl_text_box is None:
            return

        raw_value = self.ttl_text_box.text.strip()

        try:
            new_ttl = int(raw_value)
        except ValueError:
            self._add_event(f"Invalid TTL value: {raw_value}")
            return

        if new_ttl < 1:
            self._add_event(f"TTL must be >= 1, got {new_ttl}")
            return

        self.initial_ttl = new_ttl
        self._restart_with_current_ttl()
        self._add_event(f"TTL changed to {new_ttl}; visualization restarted")

    def _restart_with_current_ttl(self) -> None:
        if self.source_node_id is None or self.destination_node_id is None:
            return

        self._reset_state()
        self._start_rreq(
            source_node_id=self.source_node_id,
            destination_node_id=self.destination_node_id,
            ttl=self.initial_ttl,
        )

        self.is_paused = False
        self.step_requested = False

    def _reset_state(self) -> None:
        self.packet_id_counter = 0
        self.current_time_step = 0
        self.active_packets = []
        self.delivered_rreq_paths = []
        self.delivered_rrep_paths = []
        self.dropped_packets = []
        self.events = []
        self.route_found = False
        self.route_discovery_finished = False

    def _next_packet_id(self) -> int:
        self.packet_id_counter += 1
        return self.packet_id_counter

    def _start_rreq(self, source_node_id: int, destination_node_id: int, ttl: int) -> None:
        if ttl <= 0:
            self._add_event(
                f"RREQ cannot start: TTL={ttl}",
                packet_type=VisualPacketType.RREQ,
                path=[source_node_id],
            )
            self.route_discovery_finished = True
            return

        source_neighbors = sorted(self.neighbors.get(source_node_id, []))

        if not source_neighbors:
            self._add_event(
                f"RREQ failed: source node {source_node_id} has no neighbors",
                packet_type=VisualPacketType.RREQ,
                path=[source_node_id],
            )
            self.route_discovery_finished = True
            return

        for neighbor_id in source_neighbors:
            packet = VisualPacket(
                packet_id=self._next_packet_id(),
                packet_type=VisualPacketType.RREQ,
                source_node_id=source_node_id,
                destination_node_id=destination_node_id,
                current_from_node_id=source_node_id,
                current_to_node_id=neighbor_id,
                path=[source_node_id, neighbor_id],
                ttl=ttl,
            )
            self.active_packets.append(packet)

        self._add_event(
            f"RREQ started from {source_node_id} to {destination_node_id}, TTL={ttl}",
            packet_type=VisualPacketType.RREQ,
            path=[source_node_id],
        )

    def _simulation_step(self) -> None:
        self.current_time_step += 1

        arrived_packets: list[VisualPacket] = []
        still_moving_packets: list[VisualPacket] = []

        for packet in self.active_packets:
            packet.progress += self.packet_speed

            if packet.progress >= 1.0:
                packet.progress = 1.0
                arrived_packets.append(packet)
            else:
                still_moving_packets.append(packet)

        self.active_packets = still_moving_packets

        for packet in arrived_packets:
            self._process_arrived_packet(packet)

        if not self.active_packets and not self.route_found:
            self.route_discovery_finished = True
            self._add_event(
                "Route discovery finished: destination is unreachable with selected TTL",
                packet_type=None,
            )

        if not self.active_packets and self.route_found:
            self.route_discovery_finished = True
            self._add_event(
                "Route discovery finished: RREP returned to source",
                packet_type=VisualPacketType.RREP,
            )

    def _process_arrived_packet(self, packet: VisualPacket) -> None:
        if packet.packet_type == VisualPacketType.RREQ:
            self._process_arrived_rreq(packet)
        elif packet.packet_type == VisualPacketType.RREP:
            self._process_arrived_rrep(packet)

    def _process_arrived_rreq(self, packet: VisualPacket) -> None:
        current_node_id = packet.current_to_node_id

        if current_node_id == packet.destination_node_id:
            packet.status = VisualPacketStatus.DELIVERED
            self.delivered_rreq_paths.append(packet.path[:])
            self.route_found = True

            self._add_event(
                f"RREQ delivered to target {current_node_id}. Path: {packet.path}",
                packet_type=VisualPacketType.RREQ,
                path=packet.path,
            )

            self._start_rrep(packet.path)
            return

        next_ttl = packet.ttl - 1

        if next_ttl <= 0:
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "TTL expired"
            self.dropped_packets.append(packet)

            self._add_event(
                f"RREQ dropped at node {current_node_id}: TTL expired. Path: {packet.path}",
                packet_type=VisualPacketType.RREQ,
                path=packet.path,
            )
            return

        next_neighbors = sorted(self.neighbors.get(current_node_id, []))
        forwarded = False

        for neighbor_id in next_neighbors:
            if neighbor_id in packet.path:
                continue

            new_packet = packet.clone_for_next_hop(
                packet_id=self._next_packet_id(),
                from_node_id=current_node_id,
                to_node_id=neighbor_id,
                ttl=next_ttl,
                path=packet.path + [neighbor_id],
            )
            self.active_packets.append(new_packet)
            forwarded = True

        if not forwarded:
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "No unvisited neighbors"
            self.dropped_packets.append(packet)

            self._add_event(
                f"RREQ dropped at node {current_node_id}: no unvisited neighbors. Path: {packet.path}",
                packet_type=VisualPacketType.RREQ,
                path=packet.path,
            )

    def _start_rrep(self, discovered_path: list[int]) -> None:
        if len(discovered_path) < 2:
            return

        reverse_path = list(reversed(discovered_path))
        from_node_id = reverse_path[0]
        to_node_id = reverse_path[1]

        packet = VisualPacket(
            packet_id=self._next_packet_id(),
            packet_type=VisualPacketType.RREP,
            source_node_id=discovered_path[0],
            destination_node_id=discovered_path[-1],
            current_from_node_id=from_node_id,
            current_to_node_id=to_node_id,
            path=reverse_path,
            ttl=self.initial_ttl,
        )
        self.active_packets.append(packet)

        self._add_event(
            f"RREP started by destination {discovered_path[-1]} back to source {discovered_path[0]}",
            packet_type=VisualPacketType.RREP,
            path=reverse_path,
        )

    def _process_arrived_rrep(self, packet: VisualPacket) -> None:
        current_node_id = packet.current_to_node_id

        if current_node_id == packet.source_node_id:
            packet.status = VisualPacketStatus.DELIVERED
            self.delivered_rrep_paths.append(packet.path[:])

            self._add_event(
                f"RREP delivered to source {current_node_id}. Reverse path: {packet.path}",
                packet_type=VisualPacketType.RREP,
                path=packet.path,
            )
            return

        next_ttl = packet.ttl - 1

        if next_ttl <= 0:
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "TTL expired"
            self.dropped_packets.append(packet)

            self._add_event(
                f"RREP dropped at node {current_node_id}: TTL expired. Path: {packet.path}",
                packet_type=VisualPacketType.RREP,
                path=packet.path,
            )
            return

        try:
            current_index = packet.path.index(current_node_id)
        except ValueError:
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "Current node is not in RREP path"
            self.dropped_packets.append(packet)
            return

        next_index = current_index + 1

        if next_index >= len(packet.path):
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "RREP path ended before reaching source"
            self.dropped_packets.append(packet)

            self._add_event(
                f"RREP dropped at node {current_node_id}: path ended before source",
                packet_type=VisualPacketType.RREP,
                path=packet.path,
            )
            return

        next_node_id = packet.path[next_index]

        if next_node_id not in self.neighbors.get(current_node_id, set()):
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "Broken reverse edge"
            self.dropped_packets.append(packet)

            self._add_event(
                f"RREP dropped at node {current_node_id}: no edge to {next_node_id}",
                packet_type=VisualPacketType.RREP,
                path=packet.path,
            )
            return

        if next_node_id in self.send_rrep_packs.get(current_node_id, []):
            packet.status = VisualPacketStatus.DROPPED
            packet.drop_reason = "RREP already sent"
            self.dropped_packets.append(packet)
            self._add_event(
                f"RREP dropped at node {current_node_id}: RREP already sent to {next_node_id}",
                packet_type=VisualPacketType.RREP,
                path=packet.path,
            )
            return

        self.send_rrep_packs[current_node_id].append(next_node_id)

        new_packet = packet.clone_for_next_hop(
            packet_id=self._next_packet_id(),
            from_node_id=current_node_id,
            to_node_id=next_node_id,
            ttl=next_ttl,
            path=packet.path,
        )
        self.active_packets.append(new_packet)

    def _add_event(
        self,
        message: str,
        packet_type: VisualPacketType | None = None,
        path: list[int] | None = None,
    ) -> None:
        self.events.append(
            VisualEvent(
                time_step=self.current_time_step,
                message=message,
                packet_type=packet_type,
                path=path or [],
            )
        )

    def _draw(self, ax: Any, show_node_ids: bool = True) -> list[Any]:
        ax.clear()
        ax.set_xlim(-30, self.place_x_size + 30)
        ax.set_ylim(self.place_y_size + 30, -30)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(self._make_title(), fontsize=13)

        self._draw_edges(ax)
        self._draw_success_paths(ax)
        self._draw_dropped_packets(ax)
        self._draw_nodes(ax, show_node_ids=show_node_ids)
        self._draw_active_packets(ax)
        self._draw_legend(ax)
        self._draw_event_log(ax)

        return []

    def _make_title(self) -> str:
        source = self.source_node_id
        destination = self.destination_node_id

        if self.route_discovery_finished and self.route_found:
            status = "route found"
        elif self.route_discovery_finished:
            status = "delivery failed"
        elif self.is_paused:
            status = "paused"
        else:
            status = "running"

        return (
            f"DSR Route Discovery: {source} → {destination} | "
            f"TTL={self.initial_ttl} | "
            f"time={self.current_time_step} | "
            f"status={status}"
        )

    def _draw_edges(self, ax: Any) -> None:
        for edge in self.edges:
            first_node = self.nodes[edge.first_node_id]
            second_node = self.nodes[edge.second_node_id]

            ax.plot(
                [first_node.x, second_node.x],
                [first_node.y, second_node.y],
                color="#7f8c8d",
                linewidth=1.2,
                alpha=0.45,
                zorder=1,
            )

    def _draw_success_paths(self, ax: Any) -> None:
        for path in self.delivered_rreq_paths:
            self._draw_path(ax, path, color="#3498db", linewidth=3.0, alpha=0.45)

        for path in self.delivered_rrep_paths:
            self._draw_path(ax, path, color="#27ae60", linewidth=3.0, alpha=0.55)

    def _draw_path(
        self,
        ax: Any,
        path: list[int],
        color: str,
        linewidth: float,
        alpha: float,
    ) -> None:
        for index in range(len(path) - 1):
            first_node = self.nodes[path[index]]
            second_node = self.nodes[path[index + 1]]

            ax.plot(
                [first_node.x, second_node.x],
                [first_node.y, second_node.y],
                color=color,
                linewidth=linewidth,
                alpha=alpha,
                zorder=2,
            )

    def _draw_nodes(self, ax: Any, show_node_ids: bool = True) -> None:
        for node in self.nodes.values():
            if node.node_id == self.source_node_id:
                color = "#2ecc71"
                size = 95
            elif node.node_id == self.destination_node_id:
                color = "#e74c3c"
                size = 95
            else:
                color = "#34495e"
                size = 45

            ax.scatter(
                node.x,
                node.y,
                s=size,
                color=color,
                edgecolors="white",
                linewidths=1.0,
                zorder=5,
            )

            if show_node_ids:
                ax.text(
                    node.x + 5,
                    node.y - 5,
                    str(node.node_id),
                    fontsize=8,
                    color="#111111",
                    zorder=6,
                )

    def _draw_active_packets(self, ax: Any) -> None:
        for packet in self.active_packets:
            from_node = self.nodes[packet.current_from_node_id]
            to_node = self.nodes[packet.current_to_node_id]

            x = from_node.x + (to_node.x - from_node.x) * packet.progress
            y = from_node.y + (to_node.y - from_node.y) * packet.progress

            if packet.packet_type == VisualPacketType.RREQ:
                color = "#3498db"
                marker = "o"
                label = "RREQ"
            else:
                color = "#27ae60"
                marker = "s"
                label = "RREP"

            ax.scatter(
                x,
                y,
                s=90,
                color=color,
                marker=marker,
                edgecolors="black",
                linewidths=0.7,
                zorder=10,
            )

            ax.text(
                x + 8,
                y - 8,
                f"{label}\nTTL={packet.ttl}",
                fontsize=7,
                color=color,
                zorder=11,
            )

    def _draw_dropped_packets(self, ax: Any) -> None:
        recent_drops = self.dropped_packets[-30:]

        for packet in recent_drops:
            node = self.nodes[packet.current_to_node_id]

            ax.scatter(
                node.x,
                node.y,
                s=150,
                color="none",
                edgecolors="#e74c3c",
                linewidths=2.2,
                marker="x",
                zorder=9,
            )

    def _draw_legend(self, ax: Any) -> None:
        legend_items = [
            ("Source", "#2ecc71"),
            ("Destination", "#e74c3c"),
            ("RREQ", "#3498db"),
            ("RREP", "#27ae60"),
            ("Drop", "#e74c3c"),
        ]

        x = 0.015
        y = 0.98

        for index, (label, color) in enumerate(legend_items):
            ax.text(
                x,
                y - index * 0.045,
                f"■ {label}",
                transform=ax.transAxes,
                fontsize=9,
                color=color,
                verticalalignment="top",
            )

    def _draw_event_log(self, ax: Any) -> None:
        recent_events = self.events[-7:]

        if not recent_events:
            return

        lines = []
        for event in recent_events:
            prefix = f"[{event.time_step}]"
            lines.append(f"{prefix} {event.message}")

        text = "\n".join(lines)

        ax.text(
            0.01,
            0.01,
            text,
            transform=ax.transAxes,
            fontsize=8,
            color="#2c3e50",
            verticalalignment="bottom",
            bbox={
                "boxstyle": "round,pad=0.4",
                "facecolor": "white",
                "edgecolor": "#bdc3c7",
                "alpha": 0.85,
            },
        )


def demo_random_network(
    source_node_id: int | None = None,
    destination_node_id: int | None = None,
    ttl: int = 8,
) -> None:
    from adhoc_net import AdHocNet

    ad_hoc_net = AdHocNet(ttl=ttl)
    ad_hoc_net.create_net()

    if source_node_id is None:
        source_node_id = ad_hoc_net._get_node_from(
            xmin=0,
            xmax=150,
            ymin=ad_hoc_net._plase_y_size / 2,
            ymax=ad_hoc_net._plase_y_size - 10,
        ).node_id

    if destination_node_id is None:
        destination_node_id = ad_hoc_net._get_node_from(
            xmin=ad_hoc_net._plase_x_size - 150,
            xmax=ad_hoc_net._plase_x_size - 2,
            ymin=ad_hoc_net._plase_y_size / 2,
            ymax=ad_hoc_net._plase_y_size - 10,
        ).node_id

    visualizer = DsrRouteVisualizer.from_adhoc_net(ad_hoc_net)
    visualizer.animate_route_discovery(
        source_node_id=source_node_id,
        destination_node_id=destination_node_id,
        ttl=ttl,
        interval_ms=40,
        packet_speed=0.08,
    )


def demo_from_xlsx(
    file_name: str,
    source_node_id: int,
    destination_node_id: int,
    ttl: int = 8,
) -> None:
    visualizer = DsrRouteVisualizer.from_xlsx(file_name=file_name, ttl=ttl)
    visualizer.animate_route_discovery(
        source_node_id=source_node_id,
        destination_node_id=destination_node_id,
        ttl=ttl,
        interval_ms=40,
        packet_speed=0.08,
    )


if __name__ == "__main__":
    demo_random_network(ttl=8)