from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper import ftp


PATH_UPLOAD_LOCAL_FILE = str(Path(__file__).resolve().parent / "upload.bin")
PATH_DOWNLOAD_LOCAL_FILE = str(Path(__file__).resolve().parent / "download.bin")
PATH_REMOTE_FILE = "/dev/LuaScript/main.lua"


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	mav_ftp_wrapper = ftp.Ftp(connection)

	mav_ftp_wrapper.reset_sessions()  # Just in case
	mav_ftp_wrapper.upload_file(PATH_UPLOAD_LOCAL_FILE, PATH_REMOTE_FILE)
	mav_ftp_wrapper.download_file(PATH_REMOTE_FILE, PATH_DOWNLOAD_LOCAL_FILE)

	with open(PATH_UPLOAD_LOCAL_FILE, 'rb') as lfu:
		with open(PATH_DOWNLOAD_LOCAL_FILE, 'rb') as dfu:
			lfu_content = lfu.read()
			dfu_content = dfu.read()

	print("content matches" if lfu_content == dfu_content else "CONTENT DOESN'T MATCH")
