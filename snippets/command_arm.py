from command import *
from connectivity import *


if __name__ == "__main__":
    command_arm(True)
    wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True, seconds=6)