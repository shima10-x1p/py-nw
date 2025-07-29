from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nw.link import Link
    from nw.packet import Packet
    from nw.network_graph import NetworkGraph


class Node:
    def __init__(self, node_id: int, address: str, network_graph: "NetworkGraph") -> None:
        """ネットワーク内のノードを表すNodeクラス

        Args:
            node_id (int): ノードの一意な識別子
            address (str): ノードのアドレス（例: IPアドレス）
            network_graph (NetworkGraph): ノードが属するネットワークグラフ
        """
        self.node_id = node_id
        self.address = address
        self.links: list[Link] = []  # ノードのリンク情報を格納するリスト
        self.network_graph = network_graph

        label = f"Node {node_id} ({address})"
        self.network_graph.add_node(node_id, label)

    def add_link(self, link: "Link") -> None:
        """ノードにリンクを追加する

        Args:
            link (Link): 追加するリンク
        """
        if link not in self.links:
            self.links.append(link)
    
    def send_packet(self, packet: "Packet") -> None:
        """ノードからパケットを送信する

        Args:
            packet (Packet): 送信するパケット
        """
        if packet.destination == self.address:
            self.receive_packet(packet)
        else:
            for link in self.links:
                next_node = link.node_x if self != link.node_x else link.node_y
                print(f"Node <{self.node_id}>: Forwarding packet from {self.address} to {next_node.address}")
                link.transfer_packet(packet, self)
                break

    def receive_packet(self, packet: "Packet") -> None:
        """ノードが受信したパケットを処理する

        Args:
            packet (Packet): 受信したパケット
        """
        print(f"Node <{self.node_id}>: Packet received at {self.address} from {packet.source}: {packet.payload}")

    def __str__(self) -> str:
        """ノードの文字列表現を返す"""
        connected_nodes = [link.node_x.node_id if self != link.node_x else link.node_y.node_id for link in self.links]
        connected_nodes_str = ', '.join(map(str, connected_nodes))
        return f"Node(id={self.node_id}, address={self.address}, connected_nodes=[{connected_nodes_str}])"
