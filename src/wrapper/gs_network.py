from pymavlink.dialects.v20 import geoscan
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # src

from connectivity import SYSID, COMPID, RECV_TIMEOUT_SEC
from generic import Logging
from pymavlink import mavutil


class GsNetwork:

	SUCCESS = mavutil.mavlink.MAV_GS_NETWORK_ACK_SUCCESS
	FAIL = mavutil.mavlink.MAV_GS_NETWORK_ACK_FAIL
	N_RECEIVE_ATTEMPTS = 2

	def __init__(self, mavlink_connection, f_force_response=True):
		self.connection = mavlink_connection

		if f_force_response:
			self.ack_none_default = mavutil.mavlink.MAV_GS_NETWORK_ACK_NONE
		else:
			self.ack_none_default = mavutil.mavlink.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE

	@staticmethod
	def _match_msgid(msgid, *messages):
		return all([m.msgid == msgid for m in messages])

	@staticmethod
	def _match_attr(a, b, *attributes):
		return all([getattr(a, attr) == getattr(b, attr) for attr in attributes])

	@staticmethod
	def _match_request_response(request, response):
		if GsNetwork._match_msgid(mavutil.mavlink.MAV_GS_NETWORK, request, response):
			match_attr = GsNetwork._match_attr(request, response, 'command', 'transport')
			is_response = response.ack not in [mavutil.mavlink.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE,
				mavutil.mavlink.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE]

			return match_attr and is_response
		else:
			raise NotImplemented()

	def _gs_network_request_response_loop(self, msg_request, f_expect_response):
		if f_expect_response:
			for iatt in range(GsNetwork.N_RECEIVE_ATTEMPTS):
				self.connection.mav.send(msg_request)
				msg_response = self.connection.recv_match(type="GS_NETWORK",
					condition=f"GS_NETWORK.ack != {mavutil.mavlink.MAV_GS_NETWORK_ACK_NONE} and \
					GS_NETWORK.ack != {mavutil.mavlink.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE}")

				if msg_response is not None:
					if GsNetwork._match_request_response(msg_request, msg_response):
						return msg_response

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
		msg = self.connection.mav.gs_network_encode(mavutil.mavlink.MAV_GS_NETWORK_COMMAND_OPEN,
			self.ack_none_default,
			mavutil.mavlink.MAV_GS_NETWORK_TRANSPORT_TCP4,
			port,
			remote_port,
			payload_len,
			payload)
		response = self._gs_network_request_response_loop(msg, True)

		response.port, response.ack
