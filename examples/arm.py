import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper.cmd_nav import CmdNav


if __name__ == "__main__":
	device_serial = sys.argv[1]
	baudrate = sys.argv[2]
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_SERIAL, serial=device_serial, baudrate=baudrate)
	cmd_nav = CmdNav(connection, 1, 1)

	print('sending ARM')
	cmd_nav.arm_disarm_send_arm()
	print('waiting for response')
	print(cmd_nav.arm_disarm_ack_recv(2))

	print("sending DISARM")
	cmd_nav.arm_disarm_send_disarm()
	print("waiting for response")
	print(cmd_nav.arm_disarm_ack_recv(2))