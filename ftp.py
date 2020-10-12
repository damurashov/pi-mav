import socket
from pymavlink.dialects.v20 import common as mavcommon
from pymavlink import mavutil
import datetime
import time
import struct

OP_None = 0
OP_TerminateSession = 1
OP_ResetSessions = 2
OP_ListDirectory = 3
OP_OpenFileRO = 4
OP_ReadFile = 5
OP_CreateFile = 6
OP_WriteFile = 7
OP_RemoveFile = 8
OP_CreateDirectory = 9
OP_RemoveDirectory = 10
OP_OpenFileWO = 11
OP_TruncateFile = 12
OP_Rename = 13
OP_CalcFileCRC32 = 14
OP_BurstReadFile = 15
OP_Ack = 128
OP_Nack = 129

# error codes
ERR_None = 0
ERR_Fail = 1
ERR_FailErrno = 2
ERR_InvalidDataSize = 3
ERR_InvalidSession = 4
ERR_NoSessionsAvailable = 5
ERR_EndOfFile = 6
ERR_UnknownCommand = 7
ERR_FileExists = 8
ERR_FileProtected = 9
ERR_FileNotFound = 10

HDR_Len = 12
MAX_Payload = 239

class FtpPayload:
	def __init__(self, seq, session, opcode, size, req_opcode, burst_complete, offset, payload):
		self.seq = seq
		self.session = session
		self.opcode = opcode
		self.size = size
		self.req_opcode = req_opcode
		self.burst_complete = burst_complete
		self.offset = offset
		self.payload = payload

	def pack(self):
		'''pack message'''
		ret = struct.pack("<HBBBBBBI", self.seq, self.session, self.opcode, self.size, self.req_opcode, self.burst_complete, 0, self.offset)
		if self.payload is not None:
			ret += self.payload
		ret = bytearray(ret)
		return ret

	def __str__(self):
		plen = 0
		if self.payload is not None:
			plen = len(self.payload)
		ret = "OP seq:%u sess:%u opcode:%d req_opcode:%u size:%u bc:%u ofs:%u plen=%u" % (self.seq,
																						  self.session,
																						  self.opcode,
																						  self.req_opcode,
																						  self.size,
																						  self.burst_complete,
																						  self.offset,
																						  plen)
		if plen > 0:
			ret += " [%u]" % self.payload[0]
		return ret


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
veh_addr = ("192.168.4.1", 8001)
mav = mavcommon.MAVLink(None)
mavconn = mavutil.mavudp('localhost:10000')

def send(msg):
	# sock.sendto(bytes(str(msg), "UTF-8"), veh_addr)
	# mavconn.write(msg)
	sock.sendto(msg, veh_addr)


def heartbeat():
	if datetime.datetime.now() - heartbeat.timelast > datetime.timedelta(seconds=1):
		heartbeat.timelast = datetime.datetime.now()
		msg_heartbeat = mav.heartbeat_encode(mavcommon.MAV_TYPE_GCS, mavcommon.MAV_AUTOPILOT_PX4, 0, 0,
											 mavcommon.MAV_STATE_ACTIVE)
		# print(msg_heartbeat.pack(mav))
		send(msg_heartbeat.pack(mav))

heartbeat.timelast = datetime.datetime.now()


def ftp_list():
	payload = [0, 0, 0, 3, 2, 9, 0, 0, 0, 0, 0, 0, ord('/'), ord('\0')]
	psuffix = [0] * (251 - len(payload))
	payload += psuffix
	msg = mav.file_transfer_protocol_encode(0, 0, 0, payload)
	msg = msg.pack(mav)
	print(msg)

	while True:
		try:
			heartbeat()
			# print(str(msg_ftp))
			send(msg)
			msgin = mav.parse_char(sock.recv(300))
			if msgin is not None and msgin.get_msgId() == mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL:
				print(msgin)
				payload = msgin.get_payload()
				payload = list(payload)
				payload = [f"{chr(i)}" for i in payload]
				print(payload)
				return
			time.sleep(0.5)
		except:
			# print(sys.exc_info()[0])
			pass

def ftp_write_file():
	file = [ord(c) for c in '/main.lua']
	payload = FtpPayload(1, 0, OP_OpenFileWO, len(file), 0, 1, 0, bytearray(file))
	print(payload.pack())
	msg = mav.file_transfer_protocol_encode(0, 0, 0, payload.pack())

	msg = msg.pack(mav)

	send(msg)
	msgin = mav.parse_char(sock.recv(300))
	if msgin is not None and msgin.get_msgId() == mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL:
		print(msgin)
		payload = msgin.get_payload()
		payload = list(payload)
		payload = [f"{chr(i)}" for i in payload]
		print(payload)
		return
	time.sleep(0.5)


if __name__ == "__main__":
	ftp_write_file()
	while True:
		try:
			# heartbeat()
			ftp_write_file()
		except:
			pass
