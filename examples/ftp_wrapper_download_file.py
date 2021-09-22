import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper import ftp


NAME_DEST_FILE = "./o.bin"
NAME_SRC_FILE = "/dev/LuaScript/main.lua"


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	mav_ftp_wrapper = ftp.Ftp(connection)

	mav_ftp_wrapper.reset_sessions()  # Just in case
	mav_ftp_wrapper.download_file(NAME_SRC_FILE, NAME_DEST_FILE)
