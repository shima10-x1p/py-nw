from typing import Any


class Packet:
    def __init__(self, source: str, destination: str, payload: Any) -> None:
        """ネットワーク内のパケットを表すPacketクラス

        Args:
            source (str): パケットの送信元アドレス
            destination (str): パケットの宛先アドレス
            payload (Any): パケットのデータペイロード
        """
        self.source = source
        self.destination = destination
        self.payload = payload

    def __str__(self) -> str:
        """パケットの文字列表現を返す"""
        return f"Packet(source={self.source}, destination={self.destination}, payload={self.payload})"

