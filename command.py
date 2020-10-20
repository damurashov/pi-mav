from common import *
from command import *

LUA_PARAM_1_RUN = 1
LUA_PARAM_1_STOP = 0

def msg_lua(param1):
	msg = mav.command_long_encode(1, 1, mavcommon.MAV_CMD_USER_1, 0, param1, 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)

def command_lua_run():
	send(msg_lua(LUA_PARAM_1_RUN))
	msgin = wait_for_message(mavcommon.MAVLINK_MSG_ID_COMMAND_ACK)
	if msgin is not None:
		print(msgin)