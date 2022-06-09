"""
Send a MAVLink `DEBUG` (254) message to trigger an event
"""

import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	debug = connection.mav.debug_encode(0, 0, 0)
	connection.mav.send(debug)
