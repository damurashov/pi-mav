from ftp import *
from command import *
import serial
import time

if __name__ == "__main__":
	# command_arm(False)
	command_takeoff()
	wait_for_message((mavcommon.MAVLINK_MSG_ID_COMMAND_ACK, mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, ), do_print=True, seconds=3)
	# wait_for_message(mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, do_print=True, seconds=3)