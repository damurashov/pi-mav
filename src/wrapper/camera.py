import sys
import pathlib
from dataclasses import dataclass
from pymavlink.dialects.v20 import geoscan, common
from pymavlink import mavutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from wrapper import camera


@dataclass
class Camera:
	mavlink_connection: object

	def wait_camera_heartbeat(self, block=True, timeout_seconds=None):
		"""
		Wait for heartbeat from some remote camera.
		:param timeout_seconds: If 0, perform blocking wait
		:return: Heartbeat message
		"""

		heartbeat = self.mavlink_connection.recv_match(type="HEARTBEAT", condition="HEARTBEAT.type==30", blocking=block,
			timeout=timeout_seconds)  # MAV_TYPE_CAMERA = 30

		return heartbeat

	def send_request_message_camera_information(self):
		message_request = self.mavlink_connection.mav.mav_command_long_encode(common.MAV_CMD_REQUEST_MESSAGE, 0,
			common.MAVLINK_MSG_ID_CAMERA_INFORMATION, 0, 0, 0, 0, 0, 0)
		self.mavlink_connection.mav.send(message_request)

	def wait_camera_information(self, block=True, timeout_seconds=None):
		pass
