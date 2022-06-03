import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)

	index = 1
	r = 1
	g = 1
	b = 1
	target_component = 1
	target_system = 1
	confirmation = 0

	msg = connection.mav.command_long_encode(target_system, target_component, common.MAV_CMD_USER_1, confirmation,
		index, r, g, b, 0, 0, 0)
	connection.mav.send(msg)