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
		:param block: Blocking call
		:param timeout_seconds: If 0, perform blocking wait
		:return: Heartbeat message
		"""

		heartbeat = self.mavlink_connection.recv_match(type="HEARTBEAT", condition="HEARTBEAT.type==30", blocking=block,
			timeout=timeout_seconds)  # MAV_TYPE_CAMERA = 30

		return heartbeat

	def send_request_message_camera_information(self):
		message_request = self.mavlink_connection.mav.command_long_encode(1, 100, common.MAV_CMD_REQUEST_MESSAGE, 0,
			common.MAVLINK_MSG_ID_CAMERA_INFORMATION, 0, 0, 0, 0, 0, 0)
		self.mavlink_connection.mav.send(message_request)

	def wait_camera_information(self, block=True, timeout_seconds=None):
		"""
		:return: Returns either `COMMAND_ACK` w/ error code, or `CAMERA_INFORMATION`.

		According to the standard, both
		messages are expected, but in case of successfully acquiring the `CAMERA_INFORMATION` message waiting for
		possibly skipped or reordered `COMMAND_ACK` makes no difference or sense.
		"""
		for i in range(3):  # https://mavlink.io/en/services/camera.html#camera-connection, we have to make 3 attempts
			message = self.mavlink_connection.recv_match(type=["COMMAND_ACK", "CAMERA_INFORMATION"],
				blocking=block, timeout=timeout_seconds)

			if message.id == common.MAVLINK_MSG_ID_CAMERA_INFORMATION:
				break
			elif message.id == common.MAVLINK_MSG_ID_COMMAND_ACK:
				if message.result != common.MAV_RESULT_ACCEPTED and message.command == common.MAV_CMD_REQUEST_MESSAGE:  # On our message request, we've received a response telling us that the request cannot be fullfilled
					break

		return message

	def send_cmd_image_start_capture_once(self):
		interval = 0
		total_images = 1
		sequence_number = 0
		message_start_capture = self.mavlink_connection.mav.command_long_encode(1, 100,
			common.MAV_CMD_IMAGE_START_CAPTURE, 0, 0, interval, total_images, sequence_number, float('nan'), float('nan'),
			float('nan'), float('nan'))
		self.mavlink_connection.mav.send(message_start_capture)

	def wait_camera_image_captured(self, block=True, timeout_seconds=None):
		for i in range(3):
			message = self.mavlink_connection.recv_match(type=["COMMAND_ACK", "CAMERA_IMAGE_CAPTURED"],
				blocking=block, timeout=timeout_seconds)

			if message.id == common.MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED:
				break
			elif message.id == common.MAVLINK_MSG_ID_COMMAND_ACK:
				if message.result != common.MAV_RESULT_ACCEPTED and message.command == common.MAV_CMD_REQUEST_MESSAGE:  # On our message request, we've received a response telling us that the request cannot be fullfilled
					break
