from connectivity import *
from command import *

LUA_PARAM_1_RUN = 1
LUA_PARAM_1_STOP = 0


def msg_lua(param1):
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_USER_1, 0, param1, 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def msg_rc_channels_override():
	msg = mav.rc_channels_override_encode(1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
	return msg.pack(mav)


def msg_arm(arm: bool):
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_COMPONENT_ARM_DISARM, 0, int(arm), 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def msg_takeoff():
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def msg_land():
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def _msg_user_1_led(index, r, g, b):
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_USER_1, 0, index, r, g, b, 0, 0, 0)
	return msg.pack(mav)


def command_land():
	send(msg_land())


def command_lua_run(run: bool):
	msg = mav.command_long_encode(1, 25, mavcommon.MAV_CMD_COMPONENT_ARM_DISARM, 0, int(run), 0, 0, 0, 0, 0, 0).pack(mav)
	send(msg)


def command_arm(arm: bool):
	send(msg_arm(arm))


def command_takeoff():
	send(msg_takeoff())


def command_user_1_led(index, r, g, b):
	send(_msg_user_1_led(index, r, g, b))


def command_wait_for_ack(seconds=4, do_print=True):
	return wait_for_message((mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), seconds, do_print)
