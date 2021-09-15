from pymavlink import mavutil
import socket
import pylog
import sys
import threading
import time

_log = pylog.Log()
_BEGIN_JPEG_PACKAGE_MARKER = b'\xff\xd8'
_END_JPEG_PACKAGE_MARKER = b'\xff\xd9'

SYSID = 0
COMPID = 0
RECV_TIMEOUT_SEC = 1


class Esp32Camera:
	"""
	Pioneer's ESP32 module implements rather peculiar connection scheme. This class encapsulates the entire complexity
	of the connection and connection maintenance processes.
	"""

	VIDEO_BUFFER_SIZE = 1024 * 64
	TARGET_IP = '192.168.4.1'
	TARGET_TCP_PORT = 8888

	def __init__(self):
		video_control_address = (Esp32Camera.TARGET_IP, Esp32Camera.TARGET_TCP_PORT)
		self.__video_control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__video_control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__video_control_socket.settimeout(5)
		self.__video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.__video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__video_socket.settimeout(5)

		self.__video_frame_buffer = bytes()
		self.__raw_video_frame = 0

		try:
			self.__video_control_socket.connect(video_control_address)
			self.__video_socket.bind(self.__video_control_socket.getsockname())
		except socket.error as e:
			_log.error([__file__, Esp32Camera, "receive_frame"], "Unable to connect to the target", possible_solutions=["Connect to the target's WiFi network"])
			sys.exit()

	def receive_frame(self):
		"""
		:return: JPEG packet, if managed to acquire one
		"""
		try:
			while True:
				self.__video_frame_buffer += self.__video_socket.recv(Esp32Camera.VIDEO_BUFFER_SIZE)
				beginning = self.__video_frame_buffer.find(_BEGIN_JPEG_PACKAGE_MARKER)
				end = self.__video_frame_buffer.find(_END_JPEG_PACKAGE_MARKER)  # TODO: search from starting pos
				if beginning != -1 and end != -1 and end > beginning:
					self.__raw_video_frame = self.__video_frame_buffer[beginning:end + 2]
					self.__video_frame_buffer = self.__video_frame_buffer[end + 2:]
					break
				else:
					_log.debug([__file__, Esp32Camera, "receive_frame"], "corrupt frame", got_number_of_bytes=len(self.__raw_video_frame))
					self.__video_frame_buffer = bytes()
					self.__raw_video_frame = bytes()
			return self.__raw_video_frame
		except socket.error as exc:
			_log.error([__file__, Esp32Camera, "receive_frame"], "Caught exception socket.error", message=str(exc))


class MavlinkHeartbeat(threading.Thread):
	"""
	Encapsulates HEARTBEAT-related functionality including various threading facilities. It also can be used to check
	connection
	"""

	HEARTBEAT_SEND_PERIOD_SECONDS = 1
	RECEIVE_PERIOD_SECONDS = 1

	def _send(self):
		self._mavlink_connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,
			mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

	def _try_receive(self, blocking=True, timeout=RECEIVE_PERIOD_SECONDS) -> bool:
		"""
		:return: True, if manages to receive a HEARTBEAT message. False otherwise
		"""
		message = self._mavlink_connection.wait_heartbeat(blocking=blocking, timeout=timeout)

		if message is None:
			return False

		self._last_received = time.time()

		return True

	def check_connection(self, timeout=RECEIVE_PERIOD_SECONDS):
		"""
		Checks connection regarding whether or not it is being run as a thread
		:return: True on active connection. False otherwise
		"""
		if not self.is_alive():
			self._send()
			return self._try_receive(timeout=timeout)
		else:
			if self._last_received is None:
				time.sleep(MavlinkHeartbeat.RECEIVE_PERIOD_SECONDS)

			if self._last_received is None:
				return False

			return time.time() - self._last_received < MavlinkHeartbeat.RECEIVE_PERIOD_SECONDS

	def _task(self):
		self._send()
		self._try_receive()
		time.sleep(MavlinkHeartbeat.HEARTBEAT_SEND_PERIOD_SECONDS)

	def __init__(self, mavlink_connection):
		threading.Thread.__init__(self, target=self._task)
		self._mavlink_connection = mavlink_connection
		self._last_received = None


class MavlinkConnection:

	PROFILE_UDP = 0

	@staticmethod
	def build_connection(profile):
		if profile == MavlinkConnection.PROFILE_UDP:
			target_ip = '192.168.4.1'
			target_udp_port = 8001

			return mavutil.mavlink_connection('udpout:%s:%s' % (target_ip, target_udp_port,))
