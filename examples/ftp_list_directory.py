import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

import connectivity
from mav_microservice import ftp
from generic import Logging


if __name__ == "__main__":
	connection = connectivity.MavlinkConnection.build_connection(connectivity.MavlinkConnection.PROFILE_UDP)
	mic_ftp = ftp.Ftp(connection)

	nak = ftp.Nak.NONE
	offset = 0
	file_path = '/'
	dir_list = []

	while nak == ftp.Nak.NONE:
		Logging.get_logger().debug(Logging.format(__file__, "offset:", offset))

		res = mic_ftp.list_directory(offset, file_path)

		if res is None:
			Logging.get_logger().info(Logging.format(__file__, "failed to receive", topics=["Conn"]))
			break

		nak, ret_dir_list = res
		dir_list += ret_dir_list
		offset += len(ret_dir_list)

		Logging.get_logger().debug(Logging.format(__file__, "nak", ftp.Nak.to_string(nak)))

	print(dir_list)
	print(nak)
