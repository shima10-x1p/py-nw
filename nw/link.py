import heapq
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nw.node import Node
    from nw.packet import Packet
    from nw.network_event_scheduler import NetworkEventScheduler

class Link:
    def __init__(self, node_x: "Node", node_y: "Node", network_event_scheduler: "NetworkEventScheduler", bandwidth: int = 10000, delay: float = 0.001, loss_rate: float = 0.0) -> None:
        """ネットワーク内のリンクを表すLinkクラス

        Args:
            node_x (Node): リンクの一端のノード
            node_y (Node): リンクのもう一端のノード
            network_event_scheduler (NetworkEventScheduler): リンクが属するネットワークイベントスケジューラ
            bandwidth (int, optional): リンクの帯域幅（デフォルトは10000）
            delay (float, optional): リンクの遅延（秒単位、デフォルトは0.001）
            loss_rate (float, optional): パケット損失率（デフォルトは0.0）
        """
        self.network_event_scheduler = network_event_scheduler
        self.node_x = node_x
        self.node_y = node_y
        self.bandwidth = bandwidth
        self.delay = delay
        self.loss_rate = loss_rate
        self.packet_queue_xy = []
        self.packet_queue_yx = []
        self.current_queue_time_xy = 0
        self.current_queue_time_yx = 0


        # ノードに対してリンクを接続
        self.node_x.add_link(self)
        self.node_y.add_link(self)

        label = f"{bandwidth / 1000000}Mbps, {delay}s"
        self.network_event_scheduler.add_link(node_x.node_id, node_y.node_id, label, self.bandwidth, self.delay)

    def enque_packet(self, packet: "Packet", from_node: "Node") -> None:
        """リンクのキューにパケットを追加する

        Args:
            packet (Packet): 追加するパケット
            from_node (Node): パケットを送信したノード
        """
        if from_node == self.node_x:
            queue = self.packet_queue_xy
            current_queue_time = self.current_queue_time_xy
        else:
            queue = self.packet_queue_yx
            current_queue_time = self.current_queue_time_yx

        packet_transfer_time = (packet.size * 8) / self.bandwidth
        dequeue_time = self.network_event_scheduler.current_time + current_queue_time
        heapq.heappush(queue, (dequeue_time, packet, from_node))
        self.add_to_queue_time(from_node, packet_transfer_time)
        if len(queue) == 1:
            self.network_event_scheduler.schedule_event(dequeue_time, self.transfer_packet, from_node)

    def transfer_packet(self, from_node: "Node") -> None:
        """リンクからパケットを転送する

        Args:
            from_node (Node): パケットを送信したノード
        """
        if from_node == self.node_x:
            queue = self.packet_queue_xy
        else:
            queue = self.packet_queue_yx

        if queue:
            dequeue_time, packet, _ = heapq.heappop(queue)
            packet_transfer_time = (packet.size * 8) / self.bandwidth

            if random.random() < self.loss_rate:
                packet.set_arrived(-1)

            next_node = self.node_x if from_node != self.node_x else self.node_y
            self.network_event_scheduler.schedule_event(self.network_event_scheduler.current_time + self.delay, next_node.receive_packet, packet)
            self.network_event_scheduler.schedule_event(dequeue_time + packet_transfer_time, self.subtract_from_queue_time, from_node, packet_transfer_time)

            if queue:
                next_packet_time = queue[0][0]
                self.network_event_scheduler.schedule_event(next_packet_time, self.transfer_packet, from_node)

    def add_to_queue_time(self, from_node: "Node", packet_transfer_time: float) -> None:
        """リンクのキュー時間を更新する

        Args:
            from_node (Node): パケットを送信したノード
            packet_transfer_time (float): パケットの転送時間
        """
        if from_node == self.node_x:
            self.current_queue_time_xy += packet_transfer_time
        else:
            self.current_queue_time_yx += packet_transfer_time

    def subtract_from_queue_time(self, from_node: "Node", packet_transfer_time: float) -> None:
        """リンクのキュー時間を減算する

        Args:
            from_node (Node): パケットを送信したノード
            packet_transfer_time (float): パケットの転送時間
        """
        if from_node == self.node_x:
            self.current_queue_time_xy -= packet_transfer_time
        else:
            self.current_queue_time_yx -= packet_transfer_time
    
    def __str__(self) -> str:
        """リンクの文字列表現を返す"""
        return f"Link(node_x={self.node_x.node_id}, node_y={self.node_y.node_id}, bandwidth={self.bandwidth}, delay={self.delay}, packet_loss={self.packet_loss})"
