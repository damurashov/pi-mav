import ftp
import connectivity
import time


def file_to_bytes(filename):
	with open(filename, 'rb') as f:
		return f.read()


def _wait_ftp_response(seconds=10, do_print=False):
	m = connectivity.wait_for_message((connectivity.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=seconds)
	if m is not None:
		m = ftp.FtpPayload.construct_from_bytes(m.get_payload())
	if do_print:
		print(f'Ftp response: {str(m)}')
	return m


def test():
	connectivity.send(ftp.msg_open_file_wo('/main.lua'))
	m = connectivity.wait_for_message((connectivity.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=30)
	print(m)
	if m is not None:
		ftp.FtpPayload.construct_from_bytes(m.get_payload())


def open_session(filename) -> int:

	while True:
		connectivity.send(ftp.msg_open_file_wo(filename))
		m = connectivity.wait_for_message((connectivity.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=0.3)

		if m is not None:
			m = ftp.FtpPayload.construct_from_bytes(m.get_payload())
		else:
			continue

		assert m.opcode == ftp.OP_Ack
		return m.session


ftp_seq = 0


def write_chunk(session, off, data: bytearray):
	# Pack and send

	# print(f'Writing chunk: \"{str(data)}\"')
	global ftp_seq

	while True:
		msg_out = ftp.msg_write_file(session, off, data)
		connectivity.send(msg_out)
		msg_in = _wait_ftp_response(seconds=2, do_print=True)
		if msg_in is not None:
			if msg_in.offset == off and msg_in.opcode == ftp.OP_Ack:
				ftp_seq += 1
				break


def ftp_reversibility_test(file_name_local):
	CHUNK_SIZE = 64

	file = file_to_bytes(file_name_local)
	sid = 0
	offset = 0
	stuck = False

	while len(file) != 0:
		if not stuck:
			chunk_out = file[:CHUNK_SIZE]
			file = file[CHUNK_SIZE:]

		print('sending')
		msg_out = ftp.msg_write_file(sid, offset, chunk_out)
		connectivity.send(msg_out)

		print('receiving')
		msg_in = _wait_ftp_response(0.5, True)
		if msg_in is None:
			continue
		chunk_in = msg_in.payload

		print(f"OFFSET: {offset}")
		print(f"msg_out length: {len(chunk_out)}")
		print(f"msg_in length: {len(msg_in.payload)}")
		print([hex(i) for i in chunk_out])
		print([hex(i) for i in chunk_in])
		print("")

		f_eq = len(chunk_in) == len(chunk_out)
		if f_eq:
			f_eq = all(i == j for i, j in zip(chunk_in, chunk_out))

		if not f_eq:
			stuck = True
			user_input = input('y to remove stuck mode')
			if 'y' in user_input.lower():
				print('exited stuck mode')
				stuck = False

		if stuck:
			continue

		offset += CHUNK_SIZE


def ftp_reversibility_test_local(file_name_local):
	CHUNK_SIZE = 64

	file = file_to_bytes(file_name_local)
	sid = 0
	offset = 0

	while len(file) != 0:
		chunk_out = file[:CHUNK_SIZE]
		file = file[CHUNK_SIZE:]

		print('sending')
		msg_out = ftp.payload_write_file(sid, offset, chunk_out)

		print(f"OFFSET: {offset}")
		print(f"chunk length: {len(chunk_out)}")
		print(f"msg. out length: {len(msg_out.payload)}")
		print([hex(i) for i in chunk_out])
		print([hex(i) for i in msg_out.payload])
		print("")

		assert chunk_out == msg_out.payload

		offset += CHUNK_SIZE


def snippet_ftp_upload_file(file_name_local, file_name_remote):
	# ftp.ftp_read_file()

	CHUNK_SIZE = 16
	file = file_to_bytes(file_name_local)
	sid = open_session(file_name_remote)
	file_initial_len = len(file)

	time_start = time.time()

	# print(f'Length: {len(file)}')

	offset = 0
	while len(file) != 0:
		# print(f'offset: {offset}')
		chunk = file[:CHUNK_SIZE]
		file = file[CHUNK_SIZE:]
		write_chunk(sid, offset, chunk)
		offset += len(chunk)

		percentage = offset / file_initial_len * 100 if file_initial_len != 0 else 0
		est_left = percentage / (time.time() - time_start)
		est_left = (100.0 - percentage) / est_left if percentage != 100.0 else 0
		print(f'{percentage} %. Est. left (sec): {est_left}')
		time.sleep(0.05)

	connectivity.send(ftp.msg_terminate_session(sid))
	print('done')


if __name__ == "__main__":
	# ftp_reversibility_test('/home/dmurashov/Documents/espcomplete/nuttx.enc12.2_0005BE3F0062958724915B839DD2D3F2.iboot')
	# ftp_reversibility_test_local('/home/dmurashov/Documents/espcomplete/nuttx.enc12.2_0005BE3F0062958724915B839DD2D3F2.iboot')
	# snippet_ftp_upload_file('/home/dmurashov/Documents/espcomplete/nuttx.enc12.2_0005BE3F0062958724915B839DD2D3F2.iboot', '/firmware.bin')
	# snippet_ftp_upload_file('/home/dmurashov/Documents/espcomplete/context2.bin', '/firmware.bin')
	snippet_ftp_upload_file('/home/dmurashov/Documents/espcomplete/nuttx.enc12.2_0005BE3F0062958724915B839DD2D3F2.iboot', '/dev/UavMonitor/6')
	# snippet_ftp_upload_file('/home/dmurashov/Documents/MavlinkScripts/snippets/hw.luac', '/main.lua')
	# snippet_ftp_upload_file('/home/dmurashov/Documents/espcomplete/nuttx.enc12.2_0005BE3F0062958724915B839DD2D3F2.iboot', '/main.lua')
	# ftp.ftp_list()
	# connectivity.send(ftp.msg_terminate_session(1))
