import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # src

from pymavlink.dialects.v20 import common


class Tunnel:

	def __init__(self, mavlink_connection):
		self.connection = mavlink_connection

	def send(self, compid, message):
		msg = self.connection.mav.tunnel_encode(1, compid, common.MAV_TUNNEL_PAYLOAD_TYPE_UNKNOWN, len(message), message)
		self.connection.mav.send(msg)