import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from connectivity import MavlinkConnection
from wrapper import gs_network as gsnet
from generic import Logging


FORCE_RESPONSE = True  # "Insist" on a response where possible


if __name__ == "__main__":
	connection = MavlinkConnection.build_connection(MavlinkConnection.PROFILE_UDP)
	gs_network = gsnet.GsNetwork(connection, FORCE_RESPONSE)
	gs_network.open_tcp4(8989)
