import sys
import pathlib
from dataclasses import dataclass, field
from pymavlink.dialects.v20 import common
from pymavlink import mavutil
from pymavlink.dialects.v20.common import MAV_CMD_COMPONENT_ARM_DISARM

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper.cmd_nav import CmdNav

if __name__ == "__main__":
	if 1:
		device_serial = sys.argv[1]
		baudrate = sys.argv[2]
		connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_SERIAL, serial=device_serial, baudrate=baudrate)
	else:
		connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)

	confirmation = 0
	requested_msg_id = common.MAVLINK_MSG_ID_AUTOPILOT_VERSION
	target_component = 1

	msg = connection.mav.command_long_encode(1, target_component, common.MAV_CMD_REQUEST_MESSAGE, confirmation, requested_msg_id, 0, 0, 0, 0, 0, 0)
	connection.mav.send(msg)

	msg = connection.recv_match(type="AUTOPILOT_VERSION", blocking=True, timeout=2)
	print(msg)
