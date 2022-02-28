import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper import gs_network as gsnet
from generic import Logging


FORCE_RESPONSE = True  # "Insist" on a response where possible
REMOTE_ENDPOINT_IP = bytes([192, 168, 4, 2])
REMOTE_ENDPOINT_PORT = 3000


def open_close_tcp(gs_network):
	gs_network.open_tcp4(8989)
	gs_network.close_tcp4(8989)


def send_tcp(gs_network):
	port, ack = gs_network.connect_tcp(REMOTE_ENDPOINT_IP, REMOTE_ENDPOINT_PORT)
	print(port)
	print(gs_network.send_tcp(b"Echo", REMOTE_ENDPOINT_IP, REMOTE_ENDPOINT_PORT, port))
	print(gs_network.send_tcp(b"Hello", REMOTE_ENDPOINT_IP, REMOTE_ENDPOINT_PORT, port))
	print(gs_network.disconnect_tcp(REMOTE_ENDPOINT_IP, REMOTE_ENDPOINT_PORT, port))
	print(port)


def open_close_udp(gs_network):
	gs_network.open_udp4(2222)
	gs_network.close_udp4(2222)


def send_udp(gs_network):
	# port, ack = gs_network.send_udp(b"Echo", REMOTE_ENDPOINT_IP, REMOTE_ENDPOINT_PORT, 2222)
	# assert 2222 == int(port)
	# ack = gs_network.close_udp4(2222)

	port, ack = gs_network.send_udp(b"Hello", REMOTE_ENDPOINT_IP, REMOTE_ENDPOINT_PORT)
	gs_network.close_udp4(port)


def get_process_received(gs_network):
	timeout_wait_seconds = 30000
	gs_network.open_tcp4(8989)
	ret = gs_network.wait_process_received(timeout_wait_seconds)
	gs_network.close_tcp4(8989)

	print(ret)


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	gs_network = gsnet.GsNetwork(connection, FORCE_RESPONSE)
	switch = 4

	{
		0: open_close_tcp,
		1: send_tcp,
		2: open_close_udp,
		3: send_udp,
		4: get_process_received,
	}[switch](gs_network)