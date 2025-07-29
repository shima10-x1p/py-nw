import uuid
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from nw.network_event_scheduler import NetworkEventScheduler


class Packet:
    def __init__(self, source: str, destination: str, header_size: int, payload_size: int, network_event_scheduler: "NetworkEventScheduler") -> None:
        """ネットワーク内のパケットを表すPacketクラス

        Args:
            source (str): パケットの送信元アドレス
            destination (str): パケットの宛先アドレス
            header_size (int): パケットのヘッダーサイズ
            payload_size (int): パケットのペイロードサイズ
            network_event_scheduler (NetworkEventScheduler): ネットワークイベントスケジューラ
        """
        self.network_event_scheduler = network_event_scheduler
        self.id = str(uuid.uuid4())
        self.header = {
            "source": source,
            "destination": destination,
        }
        self.payload = "X" * payload_size
        self.size = header_size + payload_size
        self.creation_time = self.network_event_scheduler.current_time
        self.arrival_time = None
    
    def set_arrived(self, arrival_time: float) -> None:
        """パケットの到着時間を設定する

        Args:
            arrival_time (float): パケットの到着時間
        """
        self.arrival_time = arrival_time

    def __lt__(self, other: Any) -> bool:
        """パケットの比較を定義する

        Args:
            other (Any): 比較対象のオブジェクト
        """
        return False

    def __str__(self) -> str:
        """パケットの文字列表現を返す"""
        return f"Packet(source={self.header['source']}, destination={self.header['destination']}, payload={self.payload})"

    