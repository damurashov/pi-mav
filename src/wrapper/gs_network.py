import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # src

from connectivity import RECV_TIMEOUT_SEC
from generic import Logging, extend_bytes_zeros, try_unpack_fields
from pymavlink.dialects.v20 import geoscan
from pymavlink import mavutil
import time

class GsNetwork:

	SUCCESS = geoscan.MAV_GS_NETWORK_ACK_SUCCESS
	FAIL = geoscan.MAV_GS_NETWORK_ACK_FAIL
	N_RECEIVE_ATTEMPTS = 6
	PAYLOAD_MAX_LEN = 247

	def __init__(self, mavlink_connection, f_force_response=True):
		self.connection = mavlink_connection

		if f_force_response:
			self.ack_none_default = geoscan.MAV_GS_NETWORK_ACK_NONE
		else:
			self.ack_none_default = geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE

		self.f_expect_response = f_force_response

	@staticmethod
	def _match_msgid(msgid, *messages):
		return all([m.id == msgid for m in messages])

	@staticmethod
	def _match_attr(a, b, *attributes):
		return all([getattr(a, attr) == getattr(b, attr) for attr in attributes])

	@staticmethod
	def _match_request_response(request, response):
		if geoscan.MAVLINK_MSG_ID_MAV_GS_NETWORK == request.id:
			match_attr = GsNetwork._match_attr(request, response, 'command', 'transport')
			is_response = response.ack not in [geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE,
				geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE]

			Logging.debug(GsNetwork._match_request_response, "request", request, "response", response, "match_attr",
				match_attr, "is_response", is_response)

			return match_attr and is_response
		else:
			raise NotImplemented()

	def _gs_network_request_response_loop(self, msg_request, f_expect_response=None):
		"""
		Makes an attempt to send a response and get a request

		:param msg_request:       MAV_GS_NETWORK message
		:param f_expect_response: Overrides self.f_expect_response
		:return:
		"""

		if f_expect_response is None:
			f_expect_response = self.f_expect_response

		if f_expect_response:
			for iatt in range(GsNetwork.N_RECEIVE_ATTEMPTS):
				self.connection.mav.send(msg_request)
				msg_response = self.connection.recv_match(type="MAV_GS_NETWORK",
					# condition=f"MAV_GS_NETWORK.ack != {geoscan.MAV_GS_NETWORK_ACK_NONE} and \
					# MAV_GS_NETWORK.ack != {geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE}",
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

	@staticmethod
	def _parse_ip(ip: bytes, proto="tcp") -> int and int:
		"""
		Based on bytes provided, infers protocol type
		:param ip:
		:param proto: {"tcp", "udp"}
		:return: (PAYLOAD LENGTH, TRANSPORT)
		"""
		payload_len = len(ip)

		assert proto in ["tcp", "udp"]
		assert payload_len in [4, 16]

		transport = {
			("tcp", 4): geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4,
			("tcp", 16): geoscan.MAV_GS_NETWORK_TRANSPORT_TCP6,
			("udp", 4): geoscan.MAV_GS_NETWORK_TRANSPORT_UDP4,
			("udp", 16): geoscan.MAV_GS_NETWORK_TRANSPORT_UDP6,
		}[(proto, payload_len)]

		return payload_len, transport

	def open(self, proto, ip_version, port):
		assert proto in ["tcp", "udp"]
		assert ip_version in [4, 6]

		transport = {
			("tcp", 4): geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4,
			("tcp", 6): geoscan.MAV_GS_NETWORK_TRANSPORT_TCP6,
			("udp", 4): geoscan.MAV_GS_NETWORK_TRANSPORT_UDP4,
			("udp", 6): geoscan.MAV_GS_NETWORK_TRANSPORT_UDP6,
		}[(proto, ip_version)]

		remote_port = 0
		payload_len = 0
		payload = b''
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_OPEN,
			self.ack_none_default,
			transport,
			port,
			remote_port,
			payload_len,
			extend_bytes_zeros(payload, GsNetwork.PAYLOAD_MAX_LEN))
		response = self._gs_network_request_response_loop(msg)

		return try_unpack_fields(response, "ack")

	def open_tcp4(self, port):
		return self.open("tcp", 4, port)

	def open_tcp6(self, port):
		return self.open("tcp", 6, port)

	def open_udp4(self, port):
		return self.open("udp", 4, port)

	def open_udp6(self, port):
		return self.open("udp", 6, port)

	def close(self, proto, ip_version, port):
		assert proto in ["tcp", "udp"]
		assert ip_version in [4, 6]

		transport = {
			("tcp", 4): geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4,
			("tcp", 6): geoscan.MAV_GS_NETWORK_TRANSPORT_TCP6,
			("udp", 4): geoscan.MAV_GS_NETWORK_TRANSPORT_UDP4,
			("udp", 6): geoscan.MAV_GS_NETWORK_TRANSPORT_UDP6,
		}[(proto, ip_version)]

		remote_port = 0
		payload_len = 0
		payload = b''
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_CLOSE,
			self.ack_none_default,
			transport,
			port,
			remote_port,
			payload_len,
			extend_bytes_zeros(payload, GsNetwork.PAYLOAD_MAX_LEN))
		response = self._gs_network_request_response_loop(msg)

		return try_unpack_fields(response, "ack")

	def close_tcp4(self, port):
		return self.close("tcp", 4, port)

	def close_tcp6(self, port):
		return self.close("tcp", 6, port)

	def close_udp4(self, port):
		return self.close("udp", 4, port)

	def close_udp6(self, port):
		return self.close("udp", 6, port)

	def send_tcp(self, payload: bytes, remote_endpoint_ip: bytes, remote_endpoint_port, local_port):
		payload_len, transport = GsNetwork._parse_ip(remote_endpoint_ip, "tcp")
		payload_len += len(payload)
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_SEND,
			self.ack_none_default,
			transport,
			local_port,
			remote_endpoint_port,
			payload_len,
			extend_bytes_zeros(remote_endpoint_ip + payload, GsNetwork.PAYLOAD_MAX_LEN)
		)
		response = self._gs_network_request_response_loop(msg)

		return try_unpack_fields(response, "ack")

	def send_udp(self, payload: bytes, remote_endpoint_ip: bytes, remote_endpoint_port, local_port=0):
		payload_len, transport = GsNetwork._parse_ip(remote_endpoint_ip, "udp")
		payload_len += len(payload)
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_SEND,
			self.ack_none_default,
			transport,
			local_port,
			remote_endpoint_port,
			payload_len,
			extend_bytes_zeros(remote_endpoint_ip + payload, GsNetwork.PAYLOAD_MAX_LEN)
		)
		response = self._gs_network_request_response_loop(msg)

		return try_unpack_fields(response, "host_port", "ack")

	def connect_tcp(self, remote_endpoint_ip: bytes, remote_endpoint_port, local_port=0):
		"""
		Made a recipient connect to a remote TCP endpoint

		:param local_port: The recepient's port
		:param remote_endpoint_ip: IP4 or IP6 address. IP version is automatically derived by its length
		:return: (PORT, ACK). PORT is the port number assigned
		"""
		payload_len, transport = GsNetwork._parse_ip(remote_endpoint_ip, "tcp")
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_CONNECT,
			self.ack_none_default,
			transport,
			local_port,
			remote_endpoint_port,
			payload_len,
			extend_bytes_zeros(remote_endpoint_ip, GsNetwork.PAYLOAD_MAX_LEN))
		response = self._gs_network_request_response_loop(msg)

		return try_unpack_fields(response, "host_port", "ack")

	def disconnect_tcp(self, remote_endpoint_ip: bytes, remote_endpoint_port, local_port):
		"""
		:param remote_endpoint_ip:   Ip of the remote point a request processor is connected to (IP version is
		                             automatically derived from its length)
		:param remote_endpoint_port:
		:param local_port:
		:return:
		"""
		payload_len, transport = GsNetwork._parse_ip(remote_endpoint_ip, "tcp")
		msg = self.connection.mav.mav_gs_network_encode(geoscan.MAV_GS_NETWORK_COMMAND_DISCONNECT,
			self.ack_none_default,
			transport,
			local_port,
			remote_endpoint_port,
			payload_len,
			extend_bytes_zeros(remote_endpoint_ip, GsNetwork.PAYLOAD_MAX_LEN))
		response = self._gs_network_request_response_loop(msg)

		return try_unpack_fields(response, "ack")

	def wait_process_received(self, timeout=RECV_TIMEOUT_SEC):
		time_end = time.time() + timeout
		msg_response = self.connection.recv_match(type="MAV_GS_NETWORK", blocking=True, timeout=timeout)
		err_message = f"Could not get a response in {timeout} seconds"

		if msg_response is None:
			raise ConnectionError(err_message)
		else:  # Kick off response messages, or those whose `command` field does not match the requested one
			f_ack = msg_response.ack in [geoscan.MAV_GS_NETWORK_ACK_NONE,
				geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE]
			f_process_received = msg_response.command == geoscan.MAV_GS_NETWORK_COMMAND_PROCESS_RECEIVED

			if not f_ack or not f_process_received:
				if time_end <= time.time():
					raise ConnectionError(err_message)
				else:
					return self.wait_process_received(time_end - time.time())

		# Parse ip

		transport_map = {
			geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4: ("tcp", 4),
			geoscan.MAV_GS_NETWORK_TRANSPORT_TCP6: ("tcp", 16),
			geoscan.MAV_GS_NETWORK_TRANSPORT_UDP4: ("udp", 4),
			geoscan.MAV_GS_NETWORK_TRANSPORT_UDP6: ("udp", 16),
		}
		proto, ip_len = transport_map[msg_response.transport]
		payload_len = msg_response.payload_len - ip_len
		payload_full = extend_bytes_zeros(bytes(msg_response.payload), GsNetwork.PAYLOAD_MAX_LEN)  # Leading zeros may be truncated
		ip = payload_full[:ip_len]
		payload = payload_full[ip_len:ip_len + payload_len]

		return proto, ip, payload

	def wait_command(self, command, timeout, expect_ip=True):
		"""
		:param command:
		:param timeout:
		:param expect_ip: If true, IP address will be decoded from `payload` field
		:return:
		"""
		Logging.debug(GsNetwork.wait_command, "timeout:", timeout)
		assert command in [
			geoscan.MAV_GS_NETWORK_COMMAND_OPEN,
			geoscan.MAV_GS_NETWORK_COMMAND_CLOSE,
			geoscan.MAV_GS_NETWORK_COMMAND_PROCESS_RECEIVED,
			geoscan.MAV_GS_NETWORK_COMMAND_PROCESS_CONNECTED,
			geoscan.MAV_GS_NETWORK_COMMAND_PROCESS_CONNECTION_ABORTED,
			geoscan.MAV_GS_NETWORK_COMMAND_CONNECT,
			geoscan.MAV_GS_NETWORK_COMMAND_DISCONNECT,
		]

		time_end = time.time() + timeout
		msg_response = self.connection.recv_match(type="MAV_GS_NETWORK", blocking=True, timeout=timeout)
		err_message = f"Could not get a response in {timeout} seconds"

		if msg_response is None:
			raise ConnectionError(err_message)
		else:  # Kick off response messages, or those whose `command` field does not match the requested one
			f_ack = msg_response.ack in [geoscan.MAV_GS_NETWORK_ACK_NONE,
				geoscan.MAV_GS_NETWORK_ACK_NONE_HOLD_RESPONSE]
			f_command = msg_response.command == command
			Logging.debug(GsNetwork.wait_command, "f_ack", f_ack, "f_command", f_command)

			if not f_ack or not f_command:
				if time_end <= time.time():
					raise ConnectionError(err_message)
				else:
					return self.wait_process_received(time_end - time.time())

		# Parse ip

		transport_map = {
			geoscan.MAV_GS_NETWORK_TRANSPORT_TCP4: ("tcp", 4),
			geoscan.MAV_GS_NETWORK_TRANSPORT_TCP6: ("tcp", 16),
			geoscan.MAV_GS_NETWORK_TRANSPORT_UDP4: ("udp", 4),
			geoscan.MAV_GS_NETWORK_TRANSPORT_UDP6: ("udp", 16),
		}
		proto, ip_len = transport_map[msg_response.transport]

		if not expect_ip:
			ip_len = 0

		payload_len = msg_response.payload_len - ip_len
		payload_full = extend_bytes_zeros(bytes(msg_response.payload), GsNetwork.PAYLOAD_MAX_LEN)  # Leading zeros may be truncated
		ip = payload_full[:ip_len]
		payload = payload_full[ip_len:ip_len + payload_len]

		return proto, ip, payload
