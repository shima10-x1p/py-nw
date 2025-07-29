from typing import TYPE_CHECKING
from nw.packet import Packet

if TYPE_CHECKING:
    from nw.link import Link
    from nw.packet import Packet
    from nw.network_event_scheduler import NetworkEventScheduler


class Node:
    def __init__(
        self,
        node_id: int,
        address: str,
        network_event_scheduler: "NetworkEventScheduler",
    ) -> None:
        """ネットワーク内のノードを表すNodeクラス

        Args:
            node_id (int): ノードの一意な識別子
            address (str): ノードのアドレス（例: IPアドレス）
            network_graph (NetworkGraph): ノードが属するネットワークグラフ
        """
        self.node_id = node_id
        self.address = address
        self.links: list[Link] = []  # ノードのリンク情報を格納するリスト
        self.network_event_scheduler = network_event_scheduler

        label = f"Node {node_id}\n({address})"
        self.network_event_scheduler.add_node(node_id, label)

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
        self.network_event_scheduler.log_packet_info(packet, "sent", self.node_id)
        if packet.header["destination"] == self.address:
            self.receive_packet(packet)
        else:
            for link in self.links:
                next_node = link.node_x if self != link.node_x else link.node_y
                link.enque_packet(packet, self)
                break

    def receive_packet(self, packet: "Packet") -> None:
        """ノードが受信したパケットを処理する

        Args:
            packet (Packet): 受信したパケット
        """
        if packet.arrival_time == -1:
            self.network_event_scheduler.log_packet_info(packet, "lost", self.node_id)
            return
        if packet.header["destination"] == self.address:
            self.network_event_scheduler.log_packet_info(
                packet, "arrived", self.node_id
            )
            packet.set_arrived(self.network_event_scheduler.current_time)
        else:
            self.network_event_scheduler.log_packet_info(
                packet, "received", self.node_id
            )
            pass

    def create_packet(
        self, destination: str, header_size: int, payload_size: int
    ) -> None:
        """ノードからパケットを作成する

        Args:
            destination (str): パケットの宛先アドレス
            header_size (int): パケットのヘッダーサイズ
            payload_size (int): パケットのペイロードサイズ

        """
        packet = Packet(
            source=self.address,
            destination=destination,
            header_size=header_size,
            payload_size=payload_size,
            network_event_scheduler=self.network_event_scheduler,
        )
        self.network_event_scheduler.log_packet_info(packet, "created", self.node_id)
        self.send_packet(packet)

    def set_traffic(
        self,
        destination: str,
        bitrate: float,
        start_time: float,
        duration: float,
        header_size: int,
        payload_size: int,
        burstiness=1.0,
    ):
        end_time = start_time + duration

        def generate_packet():
            if self.network_event_scheduler.current_time < end_time:
                self.create_packet(destination, header_size, payload_size)
                packet_size = header_size + payload_size
                interval = (packet_size * 8) / bitrate * burstiness
                self.network_event_scheduler.schedule_event(
                    self.network_event_scheduler.current_time + interval,
                    generate_packet,
                )

        self.network_event_scheduler.schedule_event(start_time, generate_packet)

    def __str__(self) -> str:
        """ノードの文字列表現を返す"""
        connected_nodes = [
            link.node_x.node_id if self != link.node_x else link.node_y.node_id
            for link in self.links
        ]
        connected_nodes_str = ", ".join(map(str, connected_nodes))
        return f"Node(id={self.node_id}, address={self.address}, connected_nodes=[{connected_nodes_str}])"
