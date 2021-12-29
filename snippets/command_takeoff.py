from command import *
import time
from generic import *


def _wait_for_ack(seconds=4, do_print=True):
    wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=do_print, seconds=seconds)


if __name__ == "__main__":
    command_arm(True)
    _wait_for_ack(2)

    command_takeoff()
    _wait_for_ack(16)

    set_position_target_local_ned()

