from connectivity import *
import threading


def msg_arm(arm: bool):
	msg = mav.command_long_encode(123, 123, mavcommon.MAV_CMD_COMPONENT_ARM_DISARM, 0, int(arm), 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def msg_rc_channels_override():
	msg = mav.rc_channels_override_encode(1, 1, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500)
	msg = msg.pack(mav)
	while True:
		send(msg)
		time.sleep(0.05)


if __name__ == "__main__":
	# t = threading.Thread(target=msg_rc_channels_override)
	# t.start()
	#
	# time.sleep(1)
	print("sending arm")
	send(msg_arm(False))
	wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True, seconds=60)