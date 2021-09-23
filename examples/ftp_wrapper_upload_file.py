from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper import ftp


NAME_SRC_FILE = str(Path(__file__).resolve().parent / "o.bin")
NAME_DEST_FILE = "/dev/LuaScript/main.lua"


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	mav_ftp_wrapper = ftp.Ftp(connection)

	mav_ftp_wrapper.reset_sessions()
	mav_ftp_wrapper.upload_file(NAME_SRC_FILE, NAME_DEST_FILE)
