import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper import camera
from pymavlink.dialects.v20 import geoscan
from generic import Logging
from pymavlink import mavutil


def print_recv_anything(conn):
	ret = conn.recv_match()

	if ret:
		print(ret)


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
	mavlink_camera = camera.Camera(connection)

	# heartbeat = mavlink_camera.wait_camera_heartbeat()
	# print(heartbeat)
	#
	# mavlink_camera.send_request_message_camera_information()
	# camera_information = mavlink_camera.wait_camera_information()
	# print(camera_information)

	mavlink_camera.send_cmd_image_start_capture_once()
	#
	# while True:
	# 	print_recv_anything(connection)

	msg_camera_image_captured = mavlink_camera.wait_camera_image_captured()
	print(msg_camera_image_captured)