"""
Send a MAVLink `DEBUG` (254) message to trigger an event
"""

import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper.cmd_nav import CmdNav
from wrapper.control import Control


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	debug = connection.mav.debug_encode(0, 0, 0)
	cmdnav = CmdNav(connection, 1, 1)
	ctl = Control(connection, 1, 1)
	connection.mav.send(debug)

	while True:
		print(ctl.recv_mission_item_reached())
		connection.mav.send(debug)
