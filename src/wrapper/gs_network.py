import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # src

from connectivity import RECV_TIMEOUT_SEC
from generic import Logging, extend_bytes_zeros
from pymavlink.dialects.v20 import geoscan
from pymavlink import mavutil


class GsNetwork:

	SUCCESS = geoscan.MAV_GS_NETWORK_ACK_SUCCESS
	FAIL = geoscan.MAV_GS_NETWORK_ACK_FAIL
	N_RECEIVE_ATTEMPTS = 3
	PAYLOAD_MAX_LEN = 247

	def __init__(self, mavlink_connection, f_force_response=True):
		self.connection = mavlink_connection

		if f_force_response:
			self.ack_none_default = geoscan.MAV_GS_NETWORK_ACK_NONE
		else:
			self.ack_none_default = geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE

	@staticmethod
	def _match_msgid(msgid, *messages):
		return all([m.msgid == msgid for m in messages])

	@staticmethod
	def _match_attr(a, b, *attributes):
		return all([getattr(a, attr) == getattr(b, attr) for attr in attributes])

	@staticmethod
	def _match_request_response(request, response):
		if GsNetwork._match_msgid(geoscan.MAV_GS_NETWORK, request, response):
			match_attr = GsNetwork._match_attr(request, response, 'command', 'transport')
			is_response = response.ack not in [geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE,
				geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE]

			return match_attr and is_response
		else:
			raise NotImplemented()

	def _gs_network_request_response_loop(self, msg_request, f_expect_response):
		if f_expect_response:
			for iatt in range(GsNetwork.N_RECEIVE_ATTEMPTS):
				self.connection.mav.send(msg_request)
				msg_response = self.connection.recv_match(type="GS_NETWORK",
					condition=f"GS_NETWORK.ack != {geoscan.MAV_GS_NETWORK_ACK_NONE} and \
					GS_NETWORK.ack != {geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE}",
					blocking=True,
					timeout=RECV_TIMEOUT_SEC)

				if msg_response is not None:
					if GsNetwork._match_request_response(msg_request, msg_response):
						return msg_response

				Logging.error(GsNetwork._gs_network_request_response_loop, f"Attempt #{iatt} - no response")

			raise ConnectionError(f"Couldn't get a response in {GsNetwork.N_RECEIVE_ATTEMPTS} attempts")
		else:
			self.connection.mav.send(msg_request)

			return None

	def open_tcp4(self, port=0) -> (int, int):
		"""
		Open IPv4 TCP socket on a remote target.

		:returns (PORT, ACK)
		"""
		remote_port = 0
		payload_len = 0
		payload = b''
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_OPEN,
			self.ack_none_default,
			geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4,
			port,
			remote_port,
			payload_len,
			extend_bytes_zeros(payload, GsNetwork.PAYLOAD_MAX_LEN))
		response = self._gs_network_request_response_loop(msg, True)

		return response.port, response.ack

	def connect_tcp4(self, remote_endpoint_ip: bytes, remote_endpoint_port, local_port=0):
		"""
		Made a recipient connect to a remote TCP endpoint

		:param local_port: The recepient's port
		:return: (PORT, ACK). PORT is the port number assigned
		"""
		payload_len = 4
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_CONNECT,
			self.ack_none_default,
			geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4,
			local_port,
			remote_endpoint_port,
			payload_len,
			extend_bytes_zeros(remote_endpoint_ip, GsNetwork.PAYLOAD_MAX_LEN))
		response = self._gs_network_request_response_loop(msg, True)

		return response.port, response.ack
