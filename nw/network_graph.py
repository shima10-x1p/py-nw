import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

class NetworkGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node_id: int, label: str) -> None:
        """グラフにノードを追加する

        Args:
            node_id (int): ノードの一意な識別子
            label (str): ノードのラベル
        """
        self.graph.add_node(node_id, label=label)

    def add_link(self, node1_id: int, node2_id: int, label: str, bandwidth: int, delay: float) -> None:
        """ノード間にリンクを追加する

        Args:
            node1_id (int): ノード1の識別子
            node2_id (int): ノード2の識別子
            label (str): リンクのラベル
            bandwidth (int): リンクの帯域幅
            delay (float): リンクの遅延
        """
        self.graph.add_edge(node1_id, node2_id, label=label, bandwidth=bandwidth, delay=delay)
    
    def draw(self) -> None:

        def get_edge_widths(bandwidths: int):
            """帯域幅に基づいてエッジの幅を計算する

            Args:
                bandwidths (int): リンクの帯域幅
            """
            return np.log10(bandwidths) + 1
        
        def get_edge_color(delay: float):
            """遅延に基づいてエッジの色を計算する

            Args:
                delay (float): リンクの遅延
            """
            if delay <= 0.001:
                return 'green'
            elif delay <= 0.01:
                return 'yellow'
            else:
                return 'red'
        
        pos = nx.spring_layout(self.graph)
        edge_widths = [get_edge_widths(self.graph[u][v]['bandwidth']) for u, v in self.graph.edges()]
        edge_colors = [get_edge_color(self.graph[u][v]['delay']) for u, v in self.graph.edges()]

        nx.draw(self.graph, pos, with_labels=False, node_color='lightblue', node_size=2000, width=edge_widths, edge_color=edge_colors)
        nx.draw_networkx_labels(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'label'))
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=nx.get_edge_attributes(self.graph, 'label'))
        plt.show()
    

