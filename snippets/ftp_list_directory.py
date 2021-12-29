import ftp
import connectivity


def _wait_ftp_response(seconds=10, do_print=False):
	m = connectivity.wait_for_message((connectivity.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=seconds)
	if m is not None:
		m = ftp.FtpPayload.construct_from_bytes(m.get_payload())
	if do_print:
		print(f'Ftp response: {str(m)}')
	return m


if __name__ == "__main__":
	ftp.ftp_list()