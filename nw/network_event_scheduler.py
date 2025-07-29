from collections import defaultdict
import heapq
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nw.packet import Packet


class NetworkEventScheduler:
    """ネットワークシミュレーション用のイベントスケジューラクラス"""

    def __init__(self, log_enabled: bool = False, verbose: bool = False):
        """
        ネットワークイベントスケジューラの初期化

        Args:
            log_enabled (bool): ロギングを有効にするかどうか
            verbose (bool): 詳細出力を有効にするかどうか
        """
        # 現在のシミュレーション時間を管理
        self.current_time = 0
        # イベントキュー（優先度付きキュー）
        self.events = []
        # イベントの一意性を保証するためのID
        self.event_id = 0
        # パケットの送受信ログを保存
        self.packet_logs = {}
        # ログ機能の有効/無効フラグ
        self.log_enabled = log_enabled
        # 詳細出力の有効/無効フラグ
        self.verbose = verbose
        # ネットワークトポロジーを表現するグラフ
        self.graph = nx.Graph()

    def add_node(self, node_id: int, label: str) -> None:
        """ネットワークにノードを追加する

        Args:
            node_id (int): ノードの一意な識別子
            label (str): ノードのラベル
        """
        self.graph.add_node(node_id, label=label)

    def add_link(
        self, node1_id: int, node2_id: int, label: str, bandwidth: int, delay: float
    ) -> None:
        """ノード間にリンクを追加する

        Args:
            node1_id (int): ノード1の識別子
            node2_id (int): ノード2の識別子
            label (str): リンクのラベル
            bandwidth (int): リンクの帯域幅
            delay (float): リンクの遅延
        """
        # グラフにエッジ（リンク）を追加し、帯域幅・遅延・ラベル属性を設定
        self.graph.add_edge(
            node1_id, node2_id, label=label, bandwidth=bandwidth, delay=delay
        )

    def draw(self) -> None:
        """ネットワークトポロジーをグラフィカルに描画する"""
        
        def get_edge_widths(bandwidths: int):
            """帯域幅に基づいてエッジの幅を計算する

            Args:
                bandwidths (int): リンクの帯域幅
            """
            # 帯域幅の対数をとって視覚的に見やすい線幅に変換
            return np.log10(bandwidths) + 1

        def get_edge_color(delay: float):
            """遅延に基づいてエッジの色を計算する

            Args:
                delay (float): リンクの遅延
            """
            # 遅延の値に応じて色分けして視覚的に分かりやすくする
            if delay <= 0.001:
                return "green"    # 低遅延（良好）
            elif delay <= 0.01:
                return "yellow"   # 中遅延（注意）
            else:
                return "red"      # 高遅延（問題）

        # ノードの位置をspring layoutアルゴリズムで自動配置
        pos = nx.spring_layout(self.graph)
        # 各エッジの帯域幅に基づいて線幅を計算
        edge_widths = [
            get_edge_widths(self.graph[u][v]["bandwidth"])
            for u, v in self.graph.edges()
        ]
        # 各エッジの遅延に基づいて色を計算
        edge_colors = [
            get_edge_color(self.graph[u][v]["delay"]) for u, v in self.graph.edges()
        ]

        # ネットワークグラフを描画
        nx.draw(
            self.graph,
            pos,
            with_labels=False,     # ノードラベルは別途描画
            node_color="lightblue", # ノードの色
            node_size=2000,        # ノードのサイズ
            width=edge_widths,     # エッジの線幅
            edge_color=edge_colors, # エッジの色
        )
        # ノードラベルを描画
        nx.draw_networkx_labels(
            self.graph, pos, labels=nx.get_node_attributes(self.graph, "label")
        )
        # エッジラベルを描画
        nx.draw_networkx_edge_labels(
            self.graph, pos, edge_labels=nx.get_edge_attributes(self.graph, "label")
        )
        # グラフを表示
        plt.show()

    def schedule_event(self, event_time: float, callback, *args) -> None:
        """イベントをスケジュールする

        Args:
            event_time (float): イベントの発生時間
            callback: イベントが発生したときに呼び出される関数
            *args: コールバック関数に渡す引数
        """
        # イベントをタプルとして作成（時間、ID、コールバック、引数）
        event = (event_time, self.event_id, callback, args)
        # 優先度付きキューにイベントを追加（時間順にソート）
        heapq.heappush(self.events, event)
        # 次のイベント用にIDをインクリメント
        self.event_id += 1

    def log_packet_info(self, packet: "Packet", event_type: str, node_id=None) -> None:
        """パケットの状態変化をログに記録する"""
        # ログ機能が有効な場合のみ処理
        if self.log_enabled:
            # パケットIDが初回の場合、ログエントリを初期化
            if packet.id not in self.packet_logs:
                self.packet_logs[packet.id] = {
                    "source": packet.header["source"],
                    "destination": packet.header["destination"],
                    "size": packet.size,
                    "creation_time": packet.creation_time,
                    "arrival_time": packet.arrival_time,
                    "events": [],
                }

            # パケット到着時は到着時刻を更新
            if event_type == "arrival":
                self.packet_logs[packet.id]["arrival_time"] = self.current_time

            # イベント情報を作成
            event_info = {
                "time": self.current_time,
                "event": event_type,
                "node_id": node_id,
                "packet_id": packet.id,
                "src": packet.header["source"],
                "dst": packet.header["destination"],
            }
            # イベントリストに追加
            self.packet_logs[packet.id]["events"].append(event_info)

            # 詳細出力が有効な場合、リアルタイムで情報を表示
            if self.verbose:
                print(
                    f"Time: {self.current_time} Node: {node_id}, Event: {event_type}, Packet: {packet.id}, Src: {packet.header['source']}, Dst: {packet.header['destination']}"
                )

    def print_packet_logs(self):
        """パケットのログを出力する"""
        # 各パケットのログを順次表示
        for packet_id, log in self.packet_logs.items():
            print(
                f"Packet ID: {packet_id} Src: {log['source']} {log['creation_time']} -> Dst: {log['destination']} {log['arrival_time']}"
            )
            # パケットの各イベントを表示
            for event in log["events"]:
                print(f"Time: {event['time']}, Event: {event['event']}")

    def generate_summary(self, packet_logs: dict):
        """パケットのログからトラフィックの概要を生成する
        Args:
            packet_logs (dict): パケットのログデータ
        """
        # 送信元-送信先ペアごとのサマリーデータを初期化
        summary_data = defaultdict(
            lambda: {
                "sent_packets": 0,       # 送信パケット数
                "sent_bytes": 0,         # 送信バイト数
                "received_packets": 0,   # 受信パケット数
                "received_bytes": 0,     # 受信バイト数
                "total_delay": 0,        # 総遅延時間
                "lost_packets": 0,       # 失われたパケット数
                "min_creation_time": float("inf"),  # 最早作成時刻
                "max_arrival_time": 0,   # 最遅到着時刻
            }
        )

        # パケットログを解析してサマリーデータを生成
        for packet_id, log in packet_logs.items():
            # 送信元-送信先ペアをキーとする
            src_dst_pair = (log["source"], log["destination"])
            # 送信統計を更新
            summary_data[src_dst_pair]["sent_packets"] += 1
            summary_data[src_dst_pair]["sent_bytes"] += log["size"]
            summary_data[src_dst_pair]["min_creation_time"] = min(
                summary_data[src_dst_pair]["min_creation_time"], log["creation_time"]
            )

            # パケットが正常に到着した場合
            if "arrival_time" in log and log["arrival_time"] is not None:
                # 受信統計を更新
                summary_data[src_dst_pair]["received_packets"] += 1
                summary_data[src_dst_pair]["received_bytes"] += log["size"]
                # 遅延時間を累積
                summary_data[src_dst_pair]["total_delay"] += (
                    log["arrival_time"] - log["creation_time"]
                )
                summary_data[src_dst_pair]["max_arrival_time"] = max(
                    summary_data[src_dst_pair]["max_arrival_time"], log["arrival_time"]
                )
            else:
                # パケットが失われた場合
                summary_data[src_dst_pair]["lost_packets"] += 1

        # サマリーデータを出力
        for src_dst, data in summary_data.items():
            # 各統計値を取得
            sent_packets = data["sent_packets"]
            sent_bytes = data["sent_bytes"]
            received_packets = data["received_packets"]
            received_bytes = data["received_bytes"]
            total_delay = data["total_delay"]
            lost_packets = data["lost_packets"]
            min_creation_time = data["min_creation_time"]
            max_arrival_time = data["max_arrival_time"]

            # 平均スループットと平均遅延を計算
            traffic_duration = max_arrival_time - min_creation_time
            avg_throughput = (
                (received_bytes * 8 / traffic_duration) if traffic_duration > 0 else 0
            )
            avg_delay = total_delay / received_packets if received_packets > 0 else 0

            # 統計情報を表示
            print(f"Src-Dst Pair: {src_dst}")
            print(f"Total Sent Packets: {sent_packets}")
            print(f"Total Sent Bytes: {sent_bytes}")
            print(f"Total Received Packets: {received_packets}")
            print(f"Total Received Bytes: {received_bytes}")
            print(f"Average Throughput (bps): {avg_throughput}")
            print(f"Average Delay (s): {avg_delay}")
            print(f"Lost Packets: {lost_packets}\n")

    def generate_throughput_graph(self, packet_logs: dict):
        """パケットのログからスループットのグラフを生成する

        Args:
            packet_logs (dict): パケットのログデータ
        """
        # 時間スロットを1秒に固定
        time_slot = 1.0

        # シミュレーション期間の最大・最小時間を計算
        max_time = max(
            log["arrival_time"]
            for log in packet_logs.values()
            if log["arrival_time"] is not None
        )
        min_time = min(log["creation_time"] for log in packet_logs.values())
        # スロットの総数を計算
        num_slots = int((max_time - min_time) / time_slot) + 1

        # 送信元-送信先ペアごとのスループットデータを収集
        throughput_data = defaultdict(list)
        for packet_id, log in packet_logs.items():
            if log["arrival_time"] is not None:
                src_dst_pair = (log["source"], log["destination"])
                # パケット到着時間からスロットインデックスを計算
                slot_index = int((log["arrival_time"] - min_time) / time_slot)
                throughput_data[src_dst_pair].append((slot_index, log["size"]))

        # 各スロットのスループットを集計
        aggregated_throughput = defaultdict(lambda: defaultdict(int))
        for src_dst, packets in throughput_data.items():
            for slot_index in range(num_slots):
                # 該当スロットのパケットサイズを合計してbpsに変換
                slot_throughput = sum(
                    size * 8 for i, size in packets if i == slot_index
                )
                aggregated_throughput[src_dst][slot_index] = slot_throughput / time_slot

        # グラフを描画
        for src_dst, slot_data in aggregated_throughput.items():
            time_slots = list(range(num_slots))
            throughputs = [slot_data[slot] for slot in time_slots]
            times = [min_time + slot * time_slot for slot in time_slots]
            # ステップグラフとして描画
            plt.step(
                times,
                throughputs,
                label=f"{src_dst[0]} -> {src_dst[1]}",
                where="post",
                linestyle="-",
                alpha=0.5,
                marker="o",
            )

        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (bps)")
        plt.title("Throughput over time")
        plt.xlim(0, max_time)
        plt.legend()
        plt.show()

    def generate_delay_histogram(self, packet_logs: dict):
        """パケットのログから遅延のヒストグラムを生成する

        Args:
            packet_logs (dict): パケットのログデータ
        """
        # 送信元-送信先ペアごとの遅延データを収集
        delay_data = defaultdict(list)
        for packet_id, log in packet_logs.items():
            if log["arrival_time"] is not None:
                src_dst_pair = (log["source"], log["destination"])
                # パケットの遅延時間を計算
                delay = log["arrival_time"] - log["creation_time"]
                delay_data[src_dst_pair].append(delay)

        # グラフの設定
        num_plots = len(delay_data)
        num_bins = 20
        fig, axs = plt.subplots(num_plots, figsize=(6, 2 * num_plots))
        # 全データの最大遅延を取得してビン幅を計算
        max_delay = max(max(delays) for delays in delay_data.values())
        bin_width = max_delay / num_bins

        # 各送信元-送信先ペアごとにヒストグラムを作成
        for i, (src_dst, delays) in enumerate(delay_data.items()):
            ax = axs[i] if num_plots > 1 else axs
            # ヒストグラムを描画
            ax.hist(
                delays,
                bins=np.arange(0, max_delay + bin_width, bin_width),
                alpha=0.5,
                color="royalblue",
                label=f"{src_dst[0]} -> {src_dst[1]}",
            )
            ax.set_xlabel("Delay (s)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Delay histogram for {src_dst[0]} -> {src_dst[1]}")
            ax.set_xlim(0, max_delay)
            ax.legend()

        plt.tight_layout()
        plt.show()

    def run(self):
        """イベントスケジューラを実行する"""
        # イベントキューが空になるまで処理を続行
        while self.events:
            # 最も早い時間のイベントを取得
            event_time, _, callback, args = heapq.heappop(self.events)
            # 現在時刻を更新
            self.current_time = event_time
            # コールバック関数を実行
            callback(*args)

    def run_until(self, end_time):
        """指定された時間までイベントを実行する

        Args:
            end_time (float): 実行を終了する時間
        """
        # 指定時間以前のイベントのみ実行
        while self.events and self.events[0][0] <= end_time:
            # 次のイベントを取得して実行
            event_time, callback, args = heapq.heappop(self.events)
            self.current_time = event_time
            callback(*args)
