from ftp import *
from command import *
from generic import *
import serial
import time


def thr():
	while True:
		wait_response(10)


t = threading.Thread(target=thr, args=())


def wait_response(seconds):
	wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True, seconds=seconds)


def yieldy():
	a = 1
	while True:
		yield a
		a = a + 1


if __name__ == "__main__":
	a = iter(yieldy())
	print(next(a))
	a = iter(a)
	print(next(a))
	# t.start()
	# time.sleep(1)
	#
	# command_lua_run(True)
	# time.sleep(3)
	#
	# command_lua_run(False)
	# time.sleep(200)
