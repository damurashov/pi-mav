from generic import *


def _wait_response(seconds=4, do_print=True):
	wait_for_message((mavcommon.MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED,), do_print=do_print, seconds=seconds)


if __name__ == "__main__":

	set_position_target_local_ned()
	_wait_response()