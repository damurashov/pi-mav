from ftp import *
from command import *
from generic import *
import serial
import time

if __name__ == "__main__":
	# while True:
	# 	wait_for_message((mavcommon.MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED,), do_print=True)
	command_arm(False)
	wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True, seconds=4)
	# command_takeoff()
	# wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True, seconds=4)
	# wait_for_message((mavcommon.MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED, ), do_print=True, seconds=4)
