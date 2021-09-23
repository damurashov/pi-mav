

"""
A wrapper over MAVLink FTP. Encapsulates CRUD-related ops.
"""

import sys
import pathlib
import os

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
	CHUNK_SIZE = 100

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

			def handle_chunk(self, chunk):
				# Write into the file if dest is not None. Accumulate result otherwise
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
			if nak == mic_ftp.Nak.NONE:
				read_state.handle_chunk(chunk)

		# Close session
		nak = self._try_receive(self.ftp.terminate_session, sid)
		mic_ftp.Nak.try_raise(nak)

		return read_state.result

	def upload_file(self, src, dest) -> type(mic_ftp.Nak.NONE):
		"""
		:param src: client-side path of type `str`, or bytes
		:param dest: server-side path
		:return: None, on success. Exception otherwise
		"""

		class WriteState:
			def __init__(self):
				assert type(src) in [str, bytes, bytearray]

				self._offset = 0
				src_path = type(src) is str and os.path.isfile(src)

				self._file = open(src, 'rb') if src_path else None

			def __del__(self):
				if self._file is not None:
					self._file.close()

			def handle_chunk(self):
				if self._file is None:
					next_chunk = src[self._offset : self._offset + Ftp.CHUNK_SIZE]
				else:
					next_chunk = self._file.read(Ftp.CHUNK_SIZE)

				off = self._offset
				self._offset += len(next_chunk)

				return off, next_chunk

		# Get a session id

		nak, sid = self._try_receive(self.ftp.open_file_wo, dest)
		mic_ftp.Nak.try_raise(nak)

		# Write a file chunk by chunk

		write_state = WriteState()
		offset, chunk = write_state.handle_chunk()

		while len(chunk):
			nak = self._try_receive(self.ftp.write_file, sid, offset, chunk)
			mic_ftp.Nak.try_raise(nak)

			offset, chunk = write_state.handle_chunk()

		# Terminate the session

		nak = self._try_receive(self.ftp.terminate_session, sid)
		mic_ftp.Nak.try_raise(nak)


	def list_directory(self, path) -> None:
		"""
		:param path: server-side path
		:return: List of directories, on successful receive. Exception otherwise
		"""
		nak = mic_ftp.Nak.NONE
		file_list = []
		read_offset = 0

		while nak == mic_ftp.Nak.NONE:
			nak, fl = self._try_receive(self.ftp.list_directory, offset=read_offset, file_path=path)
			file_list += fl
			mic_ftp.Nak.try_raise(nak)
			read_offset += len(fl)

		return file_list

	def reset_sessions(self):
		nak = self._try_receive(self.ftp.reset_sessions)
