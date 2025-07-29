from nw.network_event_scheduler import NetworkEventScheduler
from nw.node import Node
from nw.link import Link
from nw.packet import Packet

network_event_scheduler = NetworkEventScheduler(log_enabled=True)

node1 = Node(node_id=1, address="192.168.100.1", network_event_scheduler=network_event_scheduler)
node2 = Node(node_id=2, address="192.168.100.2", network_event_scheduler=network_event_scheduler)
link1 = Link(node1, node2, bandwidth=10000, delay=0.001, loss_rate=0.0, network_event_scheduler=network_event_scheduler)

network_event_scheduler.draw()

header_size = 40
payload_size = 85

node1.set_traffic(
    destination="192.168.100.2",
    bitrate=1000,
    start_time=1.0,
    duration=10.0,
    header_size=header_size,
    payload_size=payload_size,
    burstiness=1.0,
)

network_event_scheduler.run()
network_event_scheduler.print_packet_logs()