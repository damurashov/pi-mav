import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # src

from pymavlink.dialects.v20 import common
from src import generic


class Tunnel:

	PAYLOAD_LEN_MAX = 128

	def __init__(self, mavlink_connection):
		self.connection = mavlink_connection

	def send(self, compid, message):
		message = bytes(message)
		message_len = len(message)
		message = generic.extend_bytes_zeros(message, Tunnel.PAYLOAD_LEN_MAX)
		msg = self.connection.mav.tunnel_encode(1, compid, common.MAV_TUNNEL_PAYLOAD_TYPE_UNKNOWN, message_len, message)
		self.connection.mav.send(msg)