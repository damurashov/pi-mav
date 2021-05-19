from pymavlink import mavutil
from pymavlink.dialects.v20.common import MAVLink
from pymavlink.dialects.v20.common import MAV_CMD_COMPONENT_ARM_DISARM, MAVLINK_MSG_ID_HEARTBEAT
import datetime
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mav = MAVLink(None)


def send(msg):
	sock.sendto(msg, ("127.0.0.1", 8001,))


def wait_for_message(response_msgids=None, seconds=4, do_print=False):
	time_end = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
	n_messages = 0
	counter = 0
	while datetime.datetime.now() < time_end:
		try:
			msgin = mav.parse_char(bytearray([]))
			if msgin is None:
				msgin = mav.parse_char(sock.recv(300))
			# if msgin is not None and msgin.get_msgId() == response_msgid:
			# 	return msgin
			if msgin is not None:
				if response_msgids is None:
					n_messages += 1
					if do_print:
						print(msgin)
					else:
						return msgin
				elif msgin.get_msgId() in response_msgids:
					n_messages += 1
					if do_print:
						print(msgin)
					else:
						return msgin
		except:
			pass
	return None


def arm():
	msg = mav.command_long_encode(1, 1, MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
	print(msg.pack(mav))
	send(msg.pack(mav))


def heartbeat():
	msg = mav.heartbeat_encode(0, 1, 1, 1, 1, 3)


if __name__ == "__main__":
	arm()
	wait_for_message((MAVLINK_MSG_ID_HEARTBEAT,), 4, True)