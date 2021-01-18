from ftp import *
from command import *
from generic import *
import serial
import time


def thr():
	while True:
		rc_channels_override()
		time.sleep(0.2)


t = threading.Thread(target=thr, args=())


def wait_response(seconds):
	wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True, seconds=seconds)
	# wait_for_message(None, do_print=True, seconds=seconds)


if __name__ == "__main__":
	# t.start()
	# time.sleep(2)

	time.sleep(1)

	command_arm(True)
	wait_response(5)

	command_takeoff()
	wait_response(30)

	set_position_target_local_ned()
	wait_response(30)

	command_land()
	wait_response(30)