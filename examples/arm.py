import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper.cmd_nav import CmdNav
from wrapper.control import Control
from pymavlink.dialects.v20.common import MAV_FRAME_LOCAL_NED, MAV_FRAME_BODY_FRD


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	cmd_nav = CmdNav(connection, 1, 1)
	control = Control(connection, 1, 1)

	print('sending ARM')
	cmd_nav.arm_disarm_send_arm()
	print('waiting for response')
	print(cmd_nav.arm_disarm_ack_recv(2))

	time.sleep(1)

	print("sending takeoff")
	cmd_nav.nav_takeoff_send()
	print('waiting for response')
	print(cmd_nav.cmd_ack_recv(2))

	time.sleep(2)

	input("> ")
	control.send_set_position_target_local_ned(x=1, y=0, z=0, frame=MAV_FRAME_BODY_FRD, x_ignore=0, y_ignore=0,
		z_ignore=0, yaw_ignore=0)

	while True:
		print(time.time())
		print(control.recv_mission_item_reached())

	# time.sleep(4)
	# print("sending DISARM")
	# cmd_nav.arm_disarm_send_disarm()
	# print("waiting for response")
	# print(cmd_nav.arm_disarm_ack_recv(2))
