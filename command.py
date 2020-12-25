from common import *
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


def command_land():
	send(msg_land())


def command_lua_run():
	send(msg_lua(LUA_PARAM_1_RUN))


def command_arm(arm: bool):
	send(msg_rc_channels_override())
	time.sleep(0.001)
	send(msg_arm(arm))

def command_takeoff():
	send(msg_takeoff())