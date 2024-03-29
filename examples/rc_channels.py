import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection


if __name__ == "__main__":
	device_serial = sys.argv[1]
	baudrate = sys.argv[2]
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_SERIAL, serial=device_serial, baudrate=baudrate)

	roll = 1500
	pitch = 1500
	yaw = 1500
	throttle = 1500
	mode = 1

	while True:
		sleep_period_seconds = .2
		connection.mav.rc_channels_override_send(1, 1, throttle, yaw, pitch, roll, mode, 0, 0, 0)
		time.sleep(sleep_period_seconds)
