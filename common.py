import socket
from pymavlink.dialects.v20 import common as mavcommon
from pymavlink import mavutil
import datetime
import time
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
veh_addr = ("192.168.4.1", 8001)
mav = mavcommon.MAVLink(None)
mavconn = mavutil.mavudp('localhost:10000')


def heartbeat():
	if datetime.datetime.now() - heartbeat.timelast > datetime.timedelta(seconds=1):
		heartbeat.timelast = datetime.datetime.now()
		msg_heartbeat = mav.heartbeat_encode(mavcommon.MAV_TYPE_GCS, mavcommon.MAV_AUTOPILOT_PX4, 0, 0,
											 mavcommon.MAV_STATE_ACTIVE)
		# print(msg_heartbeat.pack(mav))
		send(msg_heartbeat.pack(mav))


heartbeat.timelast = datetime.datetime.now()


def wait_for_message(response_msgids=None, seconds=4, n_max_messages=2, do_print=False):
	time_end = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
	n_messages = 0
	while datetime.datetime.now() < time_end:
		heartbeat()
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
	return None


def send(msg):
	# sock.sendto(bytes(str(msg), "UTF-8"), veh_addr)
	# mavconn.write(msg)
	sock.sendto(msg, veh_addr)