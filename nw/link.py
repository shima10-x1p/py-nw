from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nw.node import Node
    from nw.packet import Packet
    from nw.network_graph import NetworkGraph

class Link:
    def __init__(self, node_x: "Node", node_y: "Node", network_graph: "NetworkGraph", bandwidth: int = 10000, delay: float = 0.001, packet_loss: float = 0.0) -> None:
        """ネットワーク内のリンクを表すLinkクラス

        Args:
            node_x (Node): リンクの一端のノード
            node_y (Node): リンクのもう一端のノード
            network_graph (NetworkGraph): リンクが属するネットワークグラフ
            bandwidth (int, optional): リンクの帯域幅（デフォルトは10000）
            delay (float, optional): リンクの遅延（秒単位、デフォルトは0.001）
            packet_loss (float, optional): パケット損失率（デフォルトは0.0）
        """
        self.node_x = node_x
        self.node_y = node_y
        self.bandwidth = bandwidth
        self.delay = delay
        self.packet_loss = packet_loss
        self.network_graph = network_graph

        # ノードに対してリンクを接続
        self.node_x.add_link(self)
        self.node_y.add_link(self)

        label = f"{bandwidth / 1000000}Mbps, {delay}s"
        self.network_graph.add_link(node_x.node_id, node_y.node_id, label, self.bandwidth, self.delay)
    
    def transfer_packet(self, packet: "Packet", from_node: "Node") -> None:
        """リンクを介してパケットを転送する

        Args:
            packet (Packet): 転送するパケット
            from_node (Node): パケットを送信したノード
        """
        next_node = self.node_x if from_node != self.node_x else self.node_y
        next_node.receive_packet(packet)
    
    def __str__(self) -> str:
        """リンクの文字列表現を返す"""
        return f"Link(node_x={self.node_x.node_id}, node_y={self.node_y.node_id}, bandwidth={self.bandwidth}, delay={self.delay}, packet_loss={self.packet_loss})"
