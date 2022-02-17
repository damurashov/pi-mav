import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper.ftp import Ftp
from mav_microservice.ftp import Nak


DIR_NAME_DEFAULT = "/dev/LuaScript"


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	ftp = Ftp(connection)
	list_directory = ftp.list_directory(DIR_NAME_DEFAULT)
	print(list_directory)