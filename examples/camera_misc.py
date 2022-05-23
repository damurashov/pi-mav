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


def run_print_recv_anything(conn):
	while True:
		print_recv_anything(conn)


def main():
	"""
	Tests basic image capture-related functionality. Dead-simple testing code, it does not make any checks for return
	types, neither does build any logic upon it, and it is not resilient to message losses. Run it a couple of times,
	if it worked once - consider it works in all cases.
	"""

	if 1:
		connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
		connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
	else:
		device_serial = sys.argv[1]
		baudrate = sys.argv[2]
		connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_SERIAL, serial=device_serial, baudrate=baudrate)

	mavlink_camera = camera.Camera(connection)

	# Wait for heartbeat from camera component
	heartbeat = mavlink_camera.wait_camera_heartbeat()
	print(heartbeat)

	# Request for camera information - what the camera can or can't do
	mavlink_camera.send_request_message_camera_information()
	camera_information = mavlink_camera.wait_camera_information()
	print(camera_information)

	# Send capture request
	mavlink_camera.send_cmd_image_start_capture_once()
	msg_camera_image_captured = mavlink_camera.wait_camera_image_captured(timeout_seconds=1)
	print(msg_camera_image_captured)

	if msg_camera_image_captured is not None:
		existing_index =  msg_camera_image_captured.image_index

	# Imitate an attempt to get a missing request notification.

	# Try to acquire a notification for a non-existing "missing" `image_index`
	mavlink_camera.send_request_camera_image_captured(image_index=9999)  # Most likely, this is a nonexistent image index, expect a failure
	msg_camera_image_captured = mavlink_camera.wait_camera_image_captured(timeout_seconds=1)
	print(msg_camera_image_captured)

	# Try the same for the existing one (note that no `None` checks are made for the index, so if the message was actually lost, this code won't work as expected)
	mavlink_camera.send_request_camera_image_captured(image_index=existing_index)
	msg_camera_image_captured = mavlink_camera.wait_camera_image_captured(timeout_seconds=1)
	print(msg_camera_image_captured)

	# Request capture status
	mavlink_camera.send_request_camera_capture_status()
	msg_camera_capture_status = mavlink_camera.wait_camera_capture_status(timeout_seconds=1)
	print(msg_camera_capture_status)


if __name__ == "__main__":
	main()
