from common import *
from command import *

LUA_PARAM_1_RUN = 1
LUA_PARAM_1_STOP = 0


def msg_lua(param1):
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_USER_1, 0, param1, 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def msg_arm(arm: bool):
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_COMPONENT_ARM_DISARM, 0, int(arm), 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def msg_takeoff():
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def command_lua_run():
	send(msg_lua(LUA_PARAM_1_RUN))


def command_arm(arm: bool):
	send(msg_arm(arm))

def command_takeoff():
	send(msg_takeoff())