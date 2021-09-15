import struct
from pymavlink.dialects.v20 import common
import sys
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # src

from connectivity import SYSID, COMPID, RECV_TIMEOUT_SEC
from generic import Logging

TARGET_NETWORK = 0


# `opcode` values
class Op:
	@staticmethod
	def to_string(val):
		rev_dict = dict((v, k) for k, v in Op.__dict__.items() if type(v) is int)
		return rev_dict[val]

	NONE = 0
	TERMINATE_SESSION = 1
	RESET_SESSIONS = 2
	LIST_DIRECTORY = 3
	OPEN_FILE_RO = 4
	READ_FILE = 5
	CREATE_FILE = 6
	WRITE_FILE = 7
	REMOVE_FILE = 8
	CREATE_DIRECTORY = 9
	REMOVE_DIRECTORY = 10
	OPEN_FILE_WO = 11
	TRUNCATE_FILE = 12
	RENAME = 13
	CALC_FILE_CRC32 = 14
	BURST_READ_FILE = 15
	ACK = 128
	NAK = 129


# Error codes
class Nak(Exception):

	@staticmethod
	def to_string(nak):
		rev_dict = dict((v, k) for k, v in Nak.__dict__.items() if type(v) is int)
		return rev_dict[nak]

	@staticmethod
	def try_raise(nak):
		"""
		:param nak: Standard MAVLink Nak code
		:return: If nak does signify a critical error, raises an appropriate exception
		"""
		if nak != Nak.NONE and nak != Nak.EOF:
			raise Nak(nak)

	def __init__(self, nak):
		Exception.__init__(Nak.to_string(nak))

	NONE = 0
	FAIL = 1
	FAIL_ERRNO = 2
	INVALID_DATA_SIZE = 3
	INVALID_SESSION = 4
	NO_SESSIONS_AVAILABLE = 5
	EOF = 6
	UNKNOWN_COMMAND = 7
	FILE_EXISTS = 8
	FILE_PROTECTED = 9
	FILE_NOT_FOUND = 10


class FtpPayload:

	OVERALL_LENGTH = 251
	PAYLOAD_LENGTH = 239
	HEADER_LENGTH = OVERALL_LENGTH - PAYLOAD_LENGTH

	def __init__(self, seq=0, session=0, opcode=0, size=0, req_opcode=0, burst_complete=0, offset=0, payload=b''):
		self.seq = seq
		self.session = session
		self.opcode = opcode
		self.size = size
		self.req_opcode = req_opcode
		self.burst_complete = burst_complete
		self.offset = offset
		self.payload = payload

	@property
	def nak(self):
		if self.opcode == Op.ACK:
			return Nak.NONE

		return int(self.payload[0])

	@staticmethod
	def construct_from_bytes(ftp_payload):
		if type(ftp_payload) is common.MAVLink_file_transfer_protocol_message:
			ftp_payload = ftp_payload.get_payload()

		ftp_payload = bytearray(ftp_payload[7:])
		if len(ftp_payload) < FtpPayload.HEADER_LENGTH:
			ftp_payload.extend(bytearray([0]) * (FtpPayload.HEADER_LENGTH - len(ftp_payload)))

		ret = struct.unpack("<HBBBBBxI", ftp_payload[0 : FtpPayload.HEADER_LENGTH])

		# Extract ftp payload (data field)
		ftp_payload = ftp_payload[FtpPayload.HEADER_LENGTH:]
		ftp_payload += b'\x00'  # Apparently, "struct.unpack" has rather inconvenient feature to cut trailing zeros
		ftp_payload = ftp_payload[:ret[3]]  # Cut the tail.

		ret = ret + (ftp_payload,)
		ret = FtpPayload(*ret)

		# print(ret)
		return ret

	def pack(self):
		"""
		:return: bytearray representation of a message
		"""
		ret = struct.pack("<HBBBBBBI", self.seq, self.session, self.opcode, self.size, self.req_opcode, self.burst_complete, 0, self.offset)
		if self.payload is not None:
			ret += bytearray(self.payload)
		remainder_length = FtpPayload.OVERALL_LENGTH - len(ret)
		ret += bytearray([0] * remainder_length)
		# ret = bytearray(ret)
		# print(len(ret))
		return ret

	def __str__(self):
		plen = 0

		if self.payload is not None:
			plen = len(self.payload)

		ret = "OP seq:%u sess:%u opcode:%d req_opcode:%u size:%u bc:%u ofs:%u plen=%u" % (self.seq,
			self.session, self.opcode, self.req_opcode, self.size, self.burst_complete, self.offset, plen)

		if plen > 0:
			ret += " [%s]" % self.payload[:]

		return ret


def increase_seq(func):

	def wrapper(self, *args, **kwargs):
		ret = func(self, *args, **kwargs)
		self.seq += 1

		return ret

	return wrapper


class Ftp:
	"""
	Wraps communication with the device over FTP sub-protocol.
	"""

	TYPE_LIST_RESPONSE_RE = r'(D|S|F)'
	NAME_LIST_RESPONSE_RE = r'([^\t\/]+)'
	SIZE_LIST_RESPONSE_RE = r'(-?[0-9]+)'
	LIST_RESPONSE_RE = TYPE_LIST_RESPONSE_RE + NAME_LIST_RESPONSE_RE + r'\t' + SIZE_LIST_RESPONSE_RE + r'\0'

	def __init__(self, connection):
		self.connection = connection
		self.seq = 0

	def send(self, payload):
		payload.seq = self.seq
		self.connection.mav.file_transfer_protocol_send(TARGET_NETWORK, SYSID, COMPID, payload.pack())

	def receive(self):
		"""
		:return: FtpPayload, or None
		"""
		# msg = self.connection.recv_match(type="FILE_TRANSFER_PROTOCOL",
		# 	condition=f"FILE_TRANSFER_PROTOCOL.seq=={self.seq}", blocking=True,
		# 	timeout=RECV_TIMEOUT_SEC)

		msg = self.connection.recv_match(type="FILE_TRANSFER_PROTOCOL", blocking=True, timeout=RECV_TIMEOUT_SEC)

		if not msg:
			Logging.get_logger().info(Logging.format(__file__, Ftp, Ftp.receive, "failed to receive", topics=['Conn']))
			return None

		return msg

	def receive_payload(self):
		"""
		Decorator over self.receive that extracts payload
		"""
		msg = self.receive()

		if not msg:
			return None

		payload = FtpPayload.construct_from_bytes(msg.get_payload())

		Logging.get_logger().debug(Logging.format(__file__, Ftp, Ftp.receive_payload,
			"Got payload:", str(payload)))

		return payload

	@increase_seq
	def list_directory(self, offset, file_path):
		"""
		:param directory: Path to the requested directory, unix-like format
		:return: (NakCode, [("D"|"F"|"S", NAME, SIZE), ...]), or None if failed to get a response
		"""
		payload = FtpPayload(opcode=Op.LIST_DIRECTORY, size=len(file_path), offset=offset,
			payload=bytearray(file_path, encoding='ascii'))
		self.send(payload)
		payload = self.receive_payload()

		# Message receiving has failed
		if not payload:
			return None

		# Payload is empty
		if payload.opcode == Op.NAK and int(payload.payload[0]) != Nak.EOF or payload.size == 0:
			return payload.opcode, []

		# Unpack directory entries from payload

		ret = []

		for m in re.finditer(Ftp.LIST_RESPONSE_RE, payload.payload.decode('ascii')):
			type = m.group(1)
			name = m.group(2)
			size = int(m.group(3))
			ret += [(type, name, size, )]

		return payload.nak, ret

	@increase_seq
	def terminate_session(self, session):
		"""
		:param session: Session ID
		:return: NakCode, or None if failed to get a response
		"""
		payload = FtpPayload(opcode=Op.TERMINATE_SESSION, session=session)
		self.send(payload)
		payload = self.receive_payload()

		if not payload:
			return None

		return payload.opcode

	@increase_seq
	def reset_sessions(self):
		"""
		:return: NakCode, or None if failed to get a response
		"""
		payload = FtpPayload(opcode=Op.RESET_SESSIONS)
		self.send(payload)
		payload=self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def open_file_ro(self, file_path):
		"""
		:param file_path: Path to the requested file, unix-like format
		:return: (NakCode, Session ID), or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.OPEN_FILE_RO, size=len(file_path),
			payload=bytearray(file_path, encoding='ascii')))
		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak, payload.session

	@increase_seq
	def read_file(self, size, session, offset):
		"""
		:param size: Size of the chunk to read
		:param session: Session ID associated with the requested file
		:param offset: Offset to read from
		:return: (NakCode, bytearray), or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.READ_FILE, size=size, session=session, offset=offset))

		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak, payload.payload

	@increase_seq
	def create_file(self, file_path):
		"""
		:param file_path: Path to the requested file, unix-like format
		:return: (NakCode, Session ID), or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.READ_FILE, size=len(file_path), payload=bytearray(file_path, encoding='ascii')))
		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak, payload.session

	@increase_seq
	def write_file(self, session, content):
		"""

		:param session: Session ID associated with the requested file
		:param content: Payload to write to the file
		:return: NakCode, or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.WRITE_FILE, size=len(content), payload=bytearray(content)))
		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def remove_file(self, file_path):
		"""
		:param file_path: Path to the requested file, unix-like format
		:return: NakCode, or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.REMOVE_FILE, size=len(file_path), payload=bytearray(file_path, encoding='ascii')))

		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def create_directory(self, dir_path):
		"""
		:param dir_path: Path to the requested file, unix-like format
		:return: NakCode, or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.CREATE_DIRECTORY, size=len(dir_path),
			payload=bytearray(dir_path, encoding='ascii')))

		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def remove_directory(self, dir_path):
		"""
		:param dir_path: Path to the requested directory, unix-like format
		:return: NakCode, or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.CREATE_DIRECTORY, size=len(dir_path),
			payload=bytearray(dir_path, encoding='ascii')))

		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def open_file_wo(self, file_path):
		"""
		:param file_path: Path to the requested file, unix-like format
		:return: (NakCode, Session ID), or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.OPEN_FILE_WO, size=len(file_path),
			payload=bytearray(file_path, encoding='ascii')))

		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak, payload.session

	@increase_seq
	def truncate_file(self, offset, file_path):
		"""
		:param offset: Offset for truncation operation
		:param file_path: Path to the requested file, unix-like format
		:return: NakCode, or None if failed to get a response
		"""
		self.send(FtpPayload(opcode=Op.TRUNCATE_FILE, size=len(file_path), offset=offset,
			payload=bytearray(file_path, encoding='ascii')))

		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def rename(self, src_file_path, dest_file_path):
		"""
		:param src_file_path: Path to the initial file, unix-like format
		:param dest_file_path: Path to the file after renaming, unix-like format
		:return: NakCode, or None if failed to get a response
		"""
		paths_packed = bytearray(src_file_path, encoding='ascii') + '\0' + bytearray(dest_file_path,
			encoding='ascii') + '\0'

		self.send(FtpPayload(opcode=Op.RENAME, size=len(paths_packed), payload=paths_packed))
		payload = self.receive_payload()

		if not payload:
			return None

		return payload.nak

	@increase_seq
	def calc_file_crc32(self, file_path):
		"""
		:param file_path: Path to the requested file, unix-like format
		:return: (NakCode, Crc32), or None if failed to get a response
		"""
		NETWORK_BYTE_ORDER = 'big'
		self.send(FtpPayload(opcode=Op.CALC_FILE_CRC32, size=len(file_path), payload=bytearray(file_path)))
		payload=self.receive_payload()

		if not payload:
			return None

		crc32 = payload[:4]
		crc32 = int.from_bytes(crc32, byteorder=NETWORK_BYTE_ORDER, signed=False)

		return payload.nak, crc32
