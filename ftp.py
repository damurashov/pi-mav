from pymavlink.dialects.v20 import common as mavcommon
from connectivity import *
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

	@staticmethod
	def construct_from_bytes(ftp_payload):
		if type(ftp_payload) is mavcommon.MAVLink_file_transfer_protocol_message:
			ftp_payload = ftp_payload.get_payload()

		ftp_payload = bytearray(ftp_payload[7:])
		if len(ftp_payload) < 12:
			ftp_payload.extend(bytearray([0]) * (12 - len(ftp_payload)))

		ret = struct.unpack("<HBBBBBxI", ftp_payload[0:12])

		# Extract ftp payload (data field)
		ftp_payload = ftp_payload[12:]
		ftp_payload = ftp_payload[:ret[3]]

		ret = ret + (ftp_payload,)
		ret = FtpPayload(*ret)

		# print(ret)
		return ret

	def pack(self):
		'''pack message'''
		ret = struct.pack("<HBBBBBBI", self.seq, self.session, self.opcode, self.size, self.req_opcode, self.burst_complete, 0, self.offset)
		if self.payload is not None:
			ret += self.payload
		remainder_length = MAX_Payload - len(ret) + 12
		if remainder_length > 0:
			ret += bytearray([0] * remainder_length)
		ret = bytearray(ret)
		# print(len(ret))
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


def msg_ftp(payload: FtpPayload):
	msg = mav.file_transfer_protocol_encode(0, 0, 0, payload.pack())
	msg = msg.pack(mav)
	return msg


def msg_open_file_wo(filename: str):
	file = [ord(c) for c in filename]
	return msg_ftp(FtpPayload(1, 0, OP_OpenFileWO, len(file), 0, 1, 0, bytearray(file)))


def msg_open_file_ro():
	# file = [ord(c) for c in '/main.lua']
	file = [ord(c) for c in '/show.bin']
	return msg_ftp(FtpPayload(1, 0, OP_OpenFileRO, len(file), 0, 1, 0, bytearray(file)))


# def msg_write_file(*args):
# 	nbytes = 4
# 	file_payload = [i for i in range(1,nbytes+1)]
# 	return msg_ftp(FtpPayload(1, 0, OP_WriteFile, len(file_payload), 0, 1, 0, bytearray(file_payload)))


def msg_write_file(sid, offset, chunk):
	return msg_ftp(FtpPayload(1, int(sid), OP_WriteFile, len(chunk), 0, 1, int(offset), bytearray(chunk)))


def msg_read_file():
	return msg_ftp(FtpPayload(1, 0, OP_ReadFile, 70, 128, 1, 0, bytearray([])))


def msg_terminate_session(sid):
	return msg_ftp(FtpPayload(1, int(sid), OP_TerminateSession, 0, 0, 0, 0, bytearray([])))


def print_ftp(msgin):
	print(msgin)
	payload = list(msgin.get_payload())
	payload = [f"{chr(i)}" for i in payload]
	print(payload[16:])


def ftp_write_file(nbytes=4):
	send(msg_open_file_wo())
	msgin = wait_for_message(mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL)
	if msgin is not None:
		print_ftp(msgin)

	send(msg_write_file(nbytes))
	msgin = wait_for_message(mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL)
	if msgin is not None:
		print_ftp(msgin)


def ftp_read_file():
	send(msg_open_file_ro())
	wait_for_message(mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL, seconds=3, do_print=True)

	send(msg_read_file())
	wait_for_message(mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL, seconds=100, do_print=True)


def wait_for_ftp_message(seconds=4, do_print=False):
	wait_for_message((mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds, do_print)