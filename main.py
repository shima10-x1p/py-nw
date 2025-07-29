from nw.network_graph import NetworkGraph
from nw.node import Node
from nw.link import Link
from nw.packet import Packet

network_graph = NetworkGraph()

node1 = Node(node_id=1, address="192.168.100.1", network_graph=network_graph)
node2 = Node(node_id=2, address="192.168.100.2", network_graph=network_graph)
node3 = Node(node_id=3, address="192.168.100.3", network_graph=network_graph)
node4 = Node(node_id=4, address="192.168.100.4", network_graph=network_graph)
link = Link(node1, node2, network_graph=network_graph)
link2 = Link(node2, node3, network_graph=network_graph, bandwidth=5000, delay=0.002)
link3 = Link(node3, node4, network_graph=network_graph, bandwidth=2000, delay=0.005)
link4 = Link(node1, node4, network_graph=network_graph, bandwidth=10000, delay=0.001)

network_graph.draw()
