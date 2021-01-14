import socket
from pymavlink.dialects.v20 import common as mavcommon
from pymavlink import mavutil
import datetime
import threading
import time
import struct
import select

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
veh_addr = ("127.0.0.1", 8000)
sock.connect(veh_addr)
sock.setblocking(0)
mav = mavcommon.MAVLink(None)
# mavconn = mavutil.mavudp('localhost:10000')


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
		ready = select.select([sock], [], [], seconds/10.0)
		if ready[0]:
			try:
				msgin = mav.parse_char(sock.recv(300))
				if msgin is not None:
					if response_msgids is None:
						if do_print:
							print(msgin)
						else:
							return msgin
					elif msgin.get_msgId() in response_msgids:
						if do_print:
							print(msgin)
						else:
							return msgin
			except mavcommon.MAVError:
				pass

lock = threading.Lock()
def send(msg):
	# sock.sendto(bytes(str(msg), "UTF-8"), veh_addr)
	# mavconn.write(msg)
	lock.acquire()
	sock.sendto(msg, veh_addr)
	lock.release()