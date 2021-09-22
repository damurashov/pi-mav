

"""
A wrapper over MAVLink FTP. Encapsulates CRUD-related ops.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from mav_microservice import ftp as mic_ftp


class Ftp:
	"""
	It handles the following aspects of communication:
	1. Connection monitoring
	2. Session management
	3. Request repetition
	"""

	# TODO: as for 2021-09-15, Geoscan MAVLink implementation kicks off file or directory creation/removal requests as those make no sense to the Autopilot. Implement relevant methods if and when it stops being the case

	N_RECEIVE_ATTEMPTS = 2
	CHUNK_SIZE = 200

	def __init__(self, mavlink_connection):
		self.ftp = mic_ftp.Ftp(mavlink_connection)

	@staticmethod
	def _try_receive(callable, *args, **kwargs):
		res = None

		for _ in range(Ftp.N_RECEIVE_ATTEMPTS):
			res = callable(*args, **kwargs)

			if res is not None:
				return res

		raise ConnectionError(f"Couldn't get a response in {Ftp.N_RECEIVE_ATTEMPTS} attempts")

	def download_file(self, src, dest) -> bytes or None:
		"""
		:param src: servers-side path
		:param dest: client-side path, or None, if the result should be stored in RAM
		:return: bytes if dest is None. None otherwise
		"""

		class ReadState:
			"""
			Manages offset shifting and file I/O, if necessary (which depends on whether `dest == None`)
			"""

			def __init__(self):
				self._file = open(dest, "wb") if dest is not None else None
				self._chunk = b''
				self.offset = 0

			@property
			def result(self):
				if dest is None:
					return None

				return self._chunk

			def __del__(self):
				if self._file is not None:
					self._file.close()

			def handle_chunk(self, nak, chunk):
				if nak != mic_ftp.Nak.NONE:  # It may be EOF or some other error. Either way, the caller should handle it
					return

				# Write if dest is not None. Accumulate result otherwise
				if dest is not None:
					self._file.write(chunk)
				else:
					self._chunk += chunk

				self.offset += len(chunk)

		# Create session
		nak, sid = self._try_receive(self.ftp.open_file_ro, src)
		mic_ftp.Nak.try_raise(nak)

		# Try to read the file

		nak = mic_ftp.Nak.NONE
		read_state = ReadState()

		while nak == mic_ftp.Nak.NONE:
			nak, chunk = self._try_receive(self.ftp.read_file, size=Ftp.CHUNK_SIZE, session=sid,
				offset=read_state.offset)
			mic_ftp.Nak.try_raise(nak)
			read_state.handle_chunk(nak, chunk)

		# Close session
		nak = self._try_receive(self.ftp.terminate_session, sid)
		mic_ftp.Nak.try_raise(nak)

		return read_state.result

	def upload_file(self, src, dest) -> type(mic_ftp.Nak.NONE):
		"""
		:param src: client-side path
		:param dest: server-side path
		:return: NakCode, on successful connection. Exception otherwise
		"""
		pass

	def list_directory(self, path) -> None:
		"""
		:param path: server-side path
		:return: List of directories, on successful receive. Exception otherwise
		"""
		nak = mic_ftp.Nak.NONE
		file_list = []
		read_offset = 0

		while nak == mic_ftp.Nak.NONE:
			nak, fl = self._try_receive(self.ftp.list_directory, offset=read_offset, file_path = path)
			file_list += fl
			mic_ftp.Nak.try_raise(nak)
			read_offset += len(file_list)

		return file_list

	def reset_sessions(self):
		nak = self._try_receive(self.ftp.reset_sessions)
